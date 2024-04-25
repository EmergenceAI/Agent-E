import json
import os
import tempfile
import traceback
from string import Template

import autogen  # type: ignore
import openai

#from autogen import Cache
from dotenv import load_dotenv

from ae.core.agents.browser_nav_agent import BrowserNavAgent
from ae.core.agents.browser_nav_agent_no_skills import BrowserNavAgentNoSkills
from ae.core.prompts import LLM_PROMPTS
from ae.utils.logger import logger


class AutogenWrapper:
    """
    A wrapper class for interacting with the Autogen library.

    Args:
        max_chat_round (int): The maximum number of chat rounds.

    Attributes:
        number_of_rounds (int): The maximum number of chat rounds.
        agents_map (dict): A dictionary of the agents that are instantiated in this autogen instance.

    """

    def __init__(self, max_chat_round: int = 50):
        self.number_of_rounds = max_chat_round
        self.agents_map: dict[str, autogen.UserProxyAgent | autogen.AssistantAgent] | None = None


    @classmethod
    async def create(cls, agents_needed: list[str] | None = None, max_chat_round: int = 50):
        """
        Create an instance of AutogenWrapper.

        Args:
            agents_needed (list[str], optional): The list of agents needed. If None, then ["user_proxy", "browser_nav_agent"] will be used.
            max_chat_round (int, optional): The maximum number of chat rounds. Defaults to 50.

        Returns:
            AutogenWrapper: An instance of AutogenWrapper.

        """
        if agents_needed is None:
            agents_needed = ["user_proxy", "browser_nav_agent"]
        # Create an instance of cls
        self = cls(max_chat_round)
        load_dotenv()
        os.environ["AUTOGEN_USE_DOCKER"] = "False"

        autogen_model_name = os.getenv("AUTOGEN_MODEL_NAME")
        if not autogen_model_name:
            autogen_model_name = "gpt-4-turbo-preview"
            logger.warning(f"Cannot find AUTOGEN_MODEL_NAME in the environment variables, setting it to default {autogen_model_name}.")

        autogen_model_api_key = os.getenv("AUTOGEN_MODEL_API_KEY")
        if autogen_model_api_key is None:
            logger.warning("Cannot find AUTOGEN_MODEL_API_KEY in the environment variables.")
            if not os.getenv('OPENAI_API_KEY'):
                logger.error("Cannot find OPENAI_API_KEY in the environment variables.")
                raise ValueError("You need to set either AUTOGEN_MODEL_API_KEY or OPENAI_API_KEY in the .env file.")
            else:
                autogen_model_api_key = os.environ['OPENAI_API_KEY']
        else:
            logger.info(f"Using model {autogen_model_name} for AutoGen from the environment variables.")
        model_info = {'model': autogen_model_name, 'api_key': autogen_model_api_key}

        if os.getenv("AUTOGEN_MODEL_BASE_URL"):
            model_info["base_url"] = os.getenv("AUTOGEN_MODEL_BASE_URL") # type: ignore

        env_var: list[dict[str, str]] = [model_info]
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp:
            json.dump(env_var, temp)
            temp_file_path = temp.name

        self.config_list = autogen.config_list_from_json(env_or_file=temp_file_path, filter_dict={"model": {autogen_model_name}}) # type: ignore
        self.agents_map = await self.__initialize_agents(agents_needed)

        return self


    async def __initialize_agents(self, agents_needed: list[str]):
        """
        Instantiate all agents with their appropriate prompts/skills.

        Args:
            agents_needed (list[str]): The list of agents needed, this list must have user_proxy in it or an error will be generated.

        Returns:
            dict: A dictionary of agent instances.

        """
        if "user_proxy" not in agents_needed:
            raise ValueError("user_proxy agent is required in the list of needed agents.")

        agents_map: dict[str, autogen.AssistantAgent | autogen.UserProxyAgent]= {}

        user_proxy_agent = await self.__create_user_proxy_agent()
        user_proxy_agent.reset()
        agents_map["user_proxy"] = user_proxy_agent
        agents_needed.remove("user_proxy")

        for agent_needed in agents_needed:
            if agent_needed == "browser_nav_agent":
                browser_nav_agent: autogen.AssistantAgent = self.__create_browser_nav_agent(user_proxy_agent)
                browser_nav_agent.reset()
                agents_map["browser_nav_agent"] = browser_nav_agent
            elif agent_needed == "browser_nav_agent_no_skills":
                browser_nav_agent_no_skills = self.__create_browser_nav_agent_no_skills(user_proxy_agent)
                browser_nav_agent_no_skills.reset()
                agents_map["browser_nav_agent_no_skills"] = browser_nav_agent_no_skills
            else:
                raise ValueError(f"Unknown agent type: {agent_needed}")

        return agents_map


    async def __create_user_proxy_agent(self):
        """
        Create a UserProxyAgent instance.

        Returns:
            autogen.UserProxyAgent: An instance of UserProxyAgent.

        """
        user_proxy_agent = autogen.UserProxyAgent(
            name="user_proxy",
            system_message=LLM_PROMPTS["USER_AGENT_PROMPT"],
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().upper().endswith("##TERMINATE##"), # type: ignore
            human_input_mode="NEVER",
            max_consecutive_auto_reply=self.number_of_rounds,
            code_execution_config={
                "last_n_messages": 1,
                "work_dir": "./",
                "use_docker": False,
            }
        )

        return user_proxy_agent

    def __create_browser_nav_agent(self, user_proxy_agent: autogen.UserProxyAgent) -> autogen.AssistantAgent:
        """
        Create a BrowserNavAgent instance.

        Args:
            user_proxy_agent (autogen.UserProxyAgent): The instance of UserProxyAgent that was created.

        Returns:
            autogen.AssistantAgent: An instance of BrowserNavAgent.

        """
        browser_nav_agent = BrowserNavAgent(self.config_list, user_proxy_agent) # type: ignore
        #print(">>> browser agent tools:", json.dumps(browser_nav_agent.agent.llm_config.get("tools"), indent=2))
        return browser_nav_agent.agent


    def __create_browser_nav_agent_no_skills(self, user_proxy_agent: autogen.UserProxyAgent):
        """
        Create a BrowserNavAgentNoSkills instance. This is mainly used for exploration at this point

        Args:
            user_proxy_agent (autogen.UserProxyAgent): The instance of UserProxyAgent that was created.

        Returns:
            autogen.AssistantAgent: An instance of BrowserNavAgentNoSkills.

        """
        browser_nav_agent_no_skills = BrowserNavAgentNoSkills(self.config_list, user_proxy_agent) # type: ignore
        return browser_nav_agent_no_skills.agent


    async def process_command(self, command: str, current_url: str | None = None):
        """
        Process a command by sending it to one or more agents.

        Args:
            command (str): The command to be processed.
            current_url (str, optional): The current URL of the browser. Defaults to None.

        """
        current_url_prompt_segment = ""
        if current_url:
            current_url_prompt_segment = f"Current URL: {current_url}"

        prompt = Template(LLM_PROMPTS["COMMAND_EXECUTION_PROMPT"]).substitute(command=command, current_url_prompt_segment=current_url_prompt_segment)
        logger.info(f"Prompt for command: {prompt}")
        #with Cache.disk() as cache:
        try:
            if self.agents_map is None:
                raise ValueError("Agents map is not initialized.")

            if "browser_nav_no_skills" in self.agents_map:
                browser_nav_agent = self.agents_map["browser_nav_agent_no_skills"]
            elif "browser_nav_agent" in self.agents_map:
                browser_nav_agent = self.agents_map["browser_nav_agent"]
            else:
                raise ValueError(f"No browser navigation agent found. in agents_map {self.agents_map}")

            await self.agents_map["user_proxy"].a_initiate_chat( # type: ignore
                browser_nav_agent, # self.manager
                #clear_history=True,
                message=prompt,
                silent=False,
                cache=None,
            )
        except openai.BadRequestError as bre:
            logger.error(f"Unable to process command: \"{command}\". {bre}")
            traceback.print_exc()
