import importlib
import os
from datetime import datetime
from string import Template
from typing import Any

import autogen  # type: ignore

from ae.core.memory.static_ltm import get_user_ltm
from ae.core.post_process_responses import reply_back_notify_overlay
from ae.core.prompts import LLM_PROMPTS
from ae.core.skills.click_using_selector import click as click_element

# from ae.core.skills.enter_text_and_click import enter_text_and_click
from ae.core.skills.enter_text_using_selector import bulk_enter_text
from ae.core.skills.enter_text_using_selector import entertext
from ae.core.skills.get_dom_with_content_type import get_dom_with_content_type
from ae.core.skills.get_url import geturl
from ae.core.skills.open_url import openurl
from ae.core.skills.pdf_text_extractor import extract_text_from_pdf

#from ae.core.skills.pdf_text_extractor import extract_text_from_pdf
from ae.core.skills.press_key_combination import press_key_combination
from ae.core.skills.skill_registry import skill_registry
from ae.utils.logger import logger


class BrowserNavAgent:
    def __init__(self, model_config_list, llm_config_params: dict[str, Any], system_prompt: str|None, browser_nav_executor: autogen.UserProxyAgent, use_planner: bool = True): # type: ignore
        """
        Initialize the BrowserNavAgent and store the AssistantAgent instance
        as an instance attribute for external access.

        Parameters:
        - model_config_list: A list of configuration parameters required for AssistantAgent.
        - llm_config_params: A dictionary of configuration parameters for the LLM.
        - system_prompt: The system prompt to be used for this agent or the default will be used if not provided.
        - user_proxy_agent: An instance of the UserProxyAgent class.
        - use_planner: (Default True) A boolean flag to indicate whether to use the planner agent or not.
        """
        self.use_planner = use_planner
        self.browser_nav_executor = browser_nav_executor
        user_ltm = self.__get_ltm()

        system_message = LLM_PROMPTS["BROWSER_AGENT_PROMPT"]
        if system_prompt and len(system_prompt) > 0:
            if isinstance(system_prompt, list):
                system_message = "\n".join(system_prompt)
            else:
                system_message = system_prompt
            logger.info(f"Using custom system prompt for BrowserNavAgent: {system_message}")

        system_message = system_message + "\n" + f"Today's date is {datetime.now().strftime('%d %B %Y')}"
        if user_ltm: #add the user LTM to the system prompt if it exists
            user_ltm = "\n" + user_ltm
            system_message = Template(system_message).substitute(basic_user_information=user_ltm)
        logger.info(f"Browser nav agent using model: {model_config_list[0]['model']}")
        self.agent = autogen.ConversableAgent(
            name="browser_navigation_agent",
            system_message=system_message,
            llm_config={
                "config_list": model_config_list,
                **llm_config_params #unpack all the name value pairs in llm_config_params as is
            },
        )
        self.__register_skills()


    def __get_ltm(self):
        """
        Get the the long term memory of the user.
        returns: str | None - The user LTM or None if not found.
        """
        return get_user_ltm()

    def __register_skills(self):
        """
        Register all the skills that the agent can perform.
        """

        # Register each skill for LLM by assistant agent and for execution by user_proxy_agen

        self.agent.register_for_llm(description=LLM_PROMPTS["OPEN_URL_PROMPT"])(openurl)
        self.browser_nav_executor.register_for_execution()(openurl)

        # self.agent.register_for_llm(description=LLM_PROMPTS["ENTER_TEXT_AND_CLICK_PROMPT"])(enter_text_and_click)
        # self.browser_nav_executor.register_for_execution()(enter_text_and_click)

        self.agent.register_for_llm(description=LLM_PROMPTS["GET_DOM_WITH_CONTENT_TYPE_PROMPT"])(get_dom_with_content_type)
        self.browser_nav_executor.register_for_execution()(get_dom_with_content_type)

        self.agent.register_for_llm(description=LLM_PROMPTS["CLICK_PROMPT"])(click_element)
        self.browser_nav_executor.register_for_execution()(click_element)

        self.agent.register_for_llm(description=LLM_PROMPTS["GET_URL_PROMPT"])(geturl)
        self.browser_nav_executor.register_for_execution()(geturl)

        self.agent.register_for_llm(description=LLM_PROMPTS["BULK_ENTER_TEXT_PROMPT"])(bulk_enter_text)
        self.browser_nav_executor.register_for_execution()(bulk_enter_text)

        self.agent.register_for_llm(description=LLM_PROMPTS["ENTER_TEXT_PROMPT"])(entertext)
        self.browser_nav_executor.register_for_execution()(entertext)

        self.agent.register_for_llm(description=LLM_PROMPTS["PRESS_KEY_COMBINATION_PROMPT"])(press_key_combination)
        self.browser_nav_executor.register_for_execution()(press_key_combination)

        self.agent.register_for_llm(description=LLM_PROMPTS["EXTRACT_TEXT_FROM_PDF_PROMPT"])(extract_text_from_pdf)
        self.browser_nav_executor.register_for_execution()(extract_text_from_pdf)

        if not self.use_planner:
            # Register reply function for printing messages to the overlay
            self.browser_nav_executor.register_reply( # type: ignore
                [autogen.Agent, None],
                reply_func=reply_back_notify_overlay,
                config={"callback": None}
            )
            self.agent.register_reply( # type: ignore
                [autogen.Agent, None],
                reply_func=reply_back_notify_overlay,
                config={"callback": None}
            )

        self.__load_additional_skills()

        #print(f">>> Function map: {self.browser_nav_executor.function_map}") # type: ignore


    def __load_additional_skills(self):
        """
        Dynamically load additional skills from directories or specific Python files
        specified by an environment variable.
        """
        # Get additional skill directories or files from environment variable
        additional_skill_dirs: str = os.getenv('ADDITIONAL_SKILL_DIRS', "")
        if len(additional_skill_dirs) == 0:
            logger.debug("No additional skill directories or files specified.")
            return

        additional_skill_paths: list[str] = additional_skill_dirs.split(',')

        for skill_path in additional_skill_paths:
            skill_path = skill_path.strip()  # Strip whitespace

            if os.path.isdir(skill_path):
                # If the path is a directory, process all .py files in it
                for filename in os.listdir(skill_path):
                    if filename.endswith(".py"):
                        module_name = filename[:-3]  # Remove .py extension
                        module_path = f"{skill_path.replace('/', '.')}.{module_name}"
                        importlib.import_module(module_path)

            elif skill_path.endswith(".py") and os.path.isfile(skill_path):
                # If the path is a specific .py file, load it directly
                module_name = os.path.basename(skill_path)[:-3]  # Strip .py extension
                directory_path = os.path.dirname(skill_path).replace('/', '.')
                module_path = f"{directory_path}.{module_name}"
                importlib.import_module(module_path)
            else:
                logger.warning(f"Invalid skill path specified: {skill_path}")

        # Register the skills that were dynamically discovered
        for skill in skill_registry:
            self.agent.register_for_llm(description=skill['description'])(skill['func'])
            self.browser_nav_executor.register_for_execution()(skill['func'])
            logger.debug(f"Registered additional skill: {skill['name']}")

