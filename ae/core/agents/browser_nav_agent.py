from datetime import datetime
from string import Template

import autogen  # type: ignore

from ae.core.memory.static_ltm import get_user_ltm
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


class BrowserNavAgent:
    def __init__(self, config_list, browser_nav_executor: autogen.UserProxyAgent): # type: ignore
        """
        Initialize the BrowserNavAgent and store the AssistantAgent instance
        as an instance attribute for external access.

        Parameters:
        - config_list: A list of configuration parameters required for AssistantAgent.
        - user_proxy_agent: An instance of the UserProxyAgent class.
        """
        self.browser_nav_executor = browser_nav_executor
        user_ltm = self.__get_ltm()
        system_message = LLM_PROMPTS["BROWSER_AGENT_PROMPT"]
        system_message = system_message + "\n" + f"Today's date is {datetime.now().strftime('%d %B %Y')}"
        if user_ltm: #add the user LTM to the system prompt if it exists
            user_ltm = "\n" + user_ltm
            system_message = Template(system_message).substitute(basic_user_information=user_ltm)

        self.agent = autogen.ConversableAgent(
            name="browser_navigation_agent",
            system_message=system_message,
            llm_config={
                "config_list": config_list,
                "cache_seed": None,
                "temperature": 0.0,
                "top_p": 0.001,
                "seed":12345
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

        # Register openurl skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["OPEN_URL_PROMPT"])(openurl)
        # Register openurl skill for execution by user_proxy_agent
        self.browser_nav_executor.register_for_execution()(openurl)

        # Register enter_text_and_click skill for LLM by assistant agent
        # self.agent.register_for_llm(description=LLM_PROMPTS["ENTER_TEXT_AND_CLICK_PROMPT"])(enter_text_and_click)
        # Register enter_text_and_click skill for execution by user_proxy_agent
        # self.browser_nav_executor.register_for_execution()(enter_text_and_click)

        # Register get_dom_with_content_type skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["GET_DOM_WITH_CONTENT_TYPE_PROMPT"])(get_dom_with_content_type)
        # Register get_dom_with_content_type skill for execution by user_proxy_agent
        self.browser_nav_executor.register_for_execution()(get_dom_with_content_type)

        # Register click_element skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["CLICK_PROMPT"])(click_element)
        # Register click_element skill for execution by user_proxy_agent
        self.browser_nav_executor.register_for_execution()(click_element)

        # Register geturl skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["GET_URL_PROMPT"])(geturl)
        # Register geturl skill for execution by user_proxy_agent
        self.browser_nav_executor.register_for_execution()(geturl)

        # Register bulk_enter_text skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["BULK_ENTER_TEXT_PROMPT"])(bulk_enter_text)
        # Register bulk_enter_text skill for execution by user_proxy_agent
        self.browser_nav_executor.register_for_execution()(bulk_enter_text)

        # Register entertext skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["ENTER_TEXT_PROMPT"])(entertext)
        # Register entertext skill for execution by user_proxy_agent
        self.browser_nav_executor.register_for_execution()(entertext)

        # Register entertext skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["PRESS_KEY_COMBINATION_PROMPT"])(press_key_combination)
        # Register entertext skill for execution by user_proxy_agent
        self.browser_nav_executor.register_for_execution()(press_key_combination)

        self.agent.register_for_llm(description=LLM_PROMPTS["EXTRACT_TEXT_FROM_PDF_PROMPT"])(extract_text_from_pdf)
        self.browser_nav_executor.register_for_execution()(extract_text_from_pdf)

        '''
        # Register reply function for printing messages
        self.browser_nav_executor.register_reply( # type: ignore
            [autogen.Agent, None],
            reply_func=print_message_from_user_proxy,
            config={"callback": None},
        )
        self.agent.register_reply( # type: ignore
            [autogen.Agent, None],
            reply_func=print_message_from_browser_agent,
            config={"callback": None},
        )
        '''
        # print(f">>> Function map: {self.browser_nav_executor.function_map}") # type: ignore
        # print(">>> Registered skills for BrowserNavAgent and BrowserNavExecutorAgent")
