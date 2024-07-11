import asyncio
import json
import os
import time

import ae.core.playwright_manager as browserManager
from ae.config import SOURCE_LOG_FOLDER_PATH
from ae.core.autogen_wrapper import AutogenWrapper
from ae.utils.cli_helper import async_input  # type: ignore
from ae.utils.http_helper import make_post_request
from ae.utils.logger import logger


class SystemOrchestrator:
    """
    Orchestrates the system's operation, handling input from both a command prompt and a web interface,
    and coordinating between the Autogen wrapper and the Playwright manager.

    Attributes:
        agent_scenario (str): The agent scenario to use for command processing. Defaults to "user_proxy,browser_nav_agent".
        input_mode (str): The input mode of the system, determining whether command prompt input is enabled. Defaults to "GUI_ONLY".
        browser_manager (PlaywrightManager): The Playwright manager instance for web interaction.
        autogen_wrapper (AutogenWrapper): The Autogen wrapper instance for agent-based command processing.
        is_running (bool): Flag indicating whether the system is currently processing a command.
        shutdown_event (asyncio.Event): Event to wait for an exit command to be processed.
    """

    def __init__(self, agent_scenario:str="user,planner_agent,browser_nav_agent,browser_nav_executor", input_mode:str="GUI_ONLY"):
        """
        Initializes the system orchestrator with the specified agent scenario and input mode.

        Args:
            agent_scenario (str, optional): The agent scenario to use for command processing. Defaults to "user_proxy,browser_nav_agent".
            input_mode (str, optional): The input mode of the system. Defaults to "GUI_ONLY".
        """
        self.agent_scenario = agent_scenario
        self.input_mode = input_mode
        self.browser_manager = None
        self.autogen_wrapper = None
        self.is_running = False

        if os.getenv('ORCHESTRATOR_API_KEY', None) is not None and os.getenv('ORCHESTRATOR_GATEWAY', None) is not None:
            self.__populate_orchestrator_info()
            logger.info(f"Orchestrator endpoint: {self.orchestrator_endpoint}")
        else:
            self.use_orchestrator = False

        self.__parse_user_and_browser_agent_names()
        self.shutdown_event = asyncio.Event() #waits for an exit command to be processed


    def __populate_orchestrator_info(self):
        """
        Populates the orchestrator information by retrieving the API key, gateway, and endpoint from environment variables.
        """
        self.orchestrator_api_key = os.getenv('ORCHESTRATOR_API_KEY')
        self.orchestrator_gateway = os.getenv('ORCHESTRATOR_GATEWAY')
        self.orchestrator_endpoint = f"{self.orchestrator_gateway}/api/orchestrate"
        self.use_orchestrator = True


    def __parse_user_and_browser_agent_names(self):
        """
        Parse the user and browser agent names from agent_scenario
        """
        self.agent_names = self.agent_scenario.split(',')
        for agent_name in self.agent_names:
            if 'user' in agent_name:
                self.ser_agent_name = agent_name
            else:
                self.browser_agent_name = agent_name

    async def initialize(self):
        """
        Initializes the components required for the system's operation, including the Autogen wrapper and the Playwright manager.
        """
        self.autogen_wrapper = await AutogenWrapper.create(agents_needed=self.agent_names)

        self.browser_manager = browserManager.PlaywrightManager(gui_input_mode=self.input_mode == "GUI_ONLY")
        await self.browser_manager.async_initialize()

        if self.input_mode == "GUI_ONLY":
            browser_context = await self.browser_manager.get_browser_context()
            await browser_context.expose_function('process_task', self.receive_command) # type: ignore

    async def start(self):
        """
        Starts the system orchestrator, initializing components and starting the command prompt loop if necessary.
        """
        await self.initialize()

        if self.input_mode != "GUI_ONLY":
            await self.command_prompt_loop()

        await self.wait_for_exit()

    async def command_prompt_loop(self):
        """
        Continuously reads and processes commands from the command prompt until an 'exit' command is received.
        """
        while not self.is_running:
            command: str = await async_input("Enter your command (or type 'exit' to quit): ") # type: ignore
            await self.process_command(command) # type: ignore

    async def receive_command(self, command: str):
        """
        Callback function to process commands received from the web interface.

        Args:
            command (str): The command received from the web interface.
        """
        await self.process_command(command)

    async def __orchestrate_command(self, command: str):
        if not self.use_orchestrator:
            return command

        orch_response = make_post_request(self.orchestrator_endpoint, {"query": command}, self.orchestrator_api_key, api_key_header_name="X-API-Key") # type: ignore

        if not orch_response:
            return command

        if "user_notification" in orch_response:
            await self.browser_manager.notify_user(orch_response["user_notification"]) # type: ignore
        if "is_terminating" in orch_response and orch_response["is_terminating"]:
            logger.info("Orchestrator indicated command execution completed.")
            return None
        if "reformulated_query" in orch_response:
            logger.info(f"Orchestrator reformulated command to: {orch_response['reformulated_query']}")
            return orch_response["reformulated_query"]


    async def process_command(self, command: str):
        """
        Processes a given command, coordinating with the Autogen wrapper for execution and handling special commands like 'exit'.

        Args:
            command (str): The command to process.
        """
        logger.info(f"Received command: {command}")
        if command.lower() == 'exit':
            await self.shutdown()
            return

        if command:
            self.is_running = True
            start_time = time.time()
            current_url = await self.browser_manager.get_current_url() if self.browser_manager else None
            self.browser_manager.ui_manager.clear_conversation_history() # type: ignore
            self.browser_manager.log_user_message(command) # type: ignore
            result = None
            logger.info(f"Processing command: {command}")
            if self.autogen_wrapper:
                await self.browser_manager.update_processing_state("processing") # type: ignore
                orchestrated_command = await self.__orchestrate_command(command)
                if orchestrated_command is not None:
                    result = await self.autogen_wrapper.process_command(orchestrated_command, current_url)
                else:
                    result = await self.autogen_wrapper.process_command(command, current_url)

                await self.browser_manager.update_processing_state("done") # type: ignore
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            logger.info(f"Command \"{command}\" took: {elapsed_time} seconds.")
            await self.save_chat_messages()
            if result is not None:
                chat_history= result.chat_history # type: ignore
                last_message = chat_history[-1] if chat_history else None # type: ignore
                if last_message and "terminate" in last_message and last_message["terminate"]=="yes":
                    await self.browser_manager.notify_user(last_message, "answer") # type: ignore

            await self.browser_manager.notify_user(f"Task Completed ({elapsed_time}s).", "info") # type: ignore
            await self.browser_manager.command_completed(command, elapsed_time) # type: ignore
            self.is_running = False

    async def save_chat_messages(self):
        """
        Saves the chat messages from the Autogen wrapper's agents to a JSON file.
        """
        messages = self.autogen_wrapper.agents_map[self.browser_agent_name].chat_messages # type: ignore
        messages_str_keys = {str(key): value for key, value in messages.items()} # type: ignore
        with open(os.path.join(SOURCE_LOG_FOLDER_PATH, 'chat_messages.json'), 'w', encoding='utf-8') as f:
            json.dump(messages_str_keys, f, ensure_ascii=False, indent=4)
        logger.debug("Chat messages saved")

    async def wait_for_exit(self):
        """
        Waits for an exit command to be processed, keeping the system active in the meantime.
        """
        await self.shutdown_event.wait()  # Wait until the shutdown event is set

    async def shutdown(self):
        """
        Shuts down the system orchestrator, stopping the Playwright manager and exiting the command prompt loop.
        """
        logger.info("Shutting down System Orchestrator...")
        if self.browser_manager:
            await self.browser_manager.stop_playwright()
        self.shutdown_event.set()  # Signal the shutdown event to stop waiting in wait_for_exit
