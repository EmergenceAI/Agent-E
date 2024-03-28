from string import Template

import autogen  # type: ignore

from ae.core.memory.static_ltm import get_user_ltm
from ae.core.post_process_responses import final_reply_callback_browser_agent as print_message_from_user_proxy  # type: ignore
from ae.core.post_process_responses import final_reply_callback_user_proxy as print_message_from_browser_agent  # type: ignore
from ae.core.prompts import LLM_PROMPTS
from ae.core.skills.click_using_selector import click as click_element
from ae.core.skills.enter_text_and_click import enter_text_and_click
from ae.core.skills.enter_text_using_selector import bulk_enter_text
from ae.core.skills.enter_text_using_selector import entertext
from ae.core.skills.get_dom_with_content_type import get_dom_with_content_type
from ae.core.skills.get_url import geturl
from ae.core.skills.get_user_input import get_user_input
from ae.core.skills.open_url import openurl


class BrowserNavAgent:
    def __init__(self, config_list, user_proxy_agent: autogen.UserProxyAgent): # type: ignore
        """
        Initialize the BrowserNavAgent and store the AssistantAgent instance
        as an instance attribute for external access.

        Parameters:
        - config_list: A list of configuration parameters required for AssistantAgent.
        - user_proxy_agent: An instance of the UserProxyAgent class.
        """
        self.user_proxy_agent = user_proxy_agent
        user_ltm = self.__get_ltm()
        system_message = LLM_PROMPTS["BROWSER_AGENT_PROMPT"]

        if user_ltm: #add the user LTM to the system prompt if it exists
            user_ltm = "\n" + user_ltm
            system_message = Template(system_message).substitute(basic_user_information=user_ltm)

        self.agent = autogen.AssistantAgent(
            name="browser_navigation_agent",
            system_message=system_message,
            llm_config={
                "config_list": config_list,
                "cache_seed": 2,
                "temperature": 0.0
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
        # Register get_user_input skill for execution by user_proxy_agent
        self.user_proxy_agent.register_for_execution()(get_user_input)
        # Register get_user_input skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["GET_USER_INPUT_PROMPT"])(get_user_input)

        # Register openurl skill for execution by user_proxy_agent
        self.user_proxy_agent.register_for_execution()(openurl)
        # Register openurl skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["OPEN_URL_PROMPT"])(openurl)

        # Register enter_text_and_click skill for execution by user_proxy_agent
        self.user_proxy_agent.register_for_execution()(enter_text_and_click)
        # Register enter_text_and_click skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["ENTER_TEXT_AND_CLICK_PROMPT"])(enter_text_and_click)

        # Register get_dom_with_content_type skill for execution by user_proxy_agent
        self.user_proxy_agent.register_for_execution()(get_dom_with_content_type)
        # Register get_dom_with_content_type skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["GET_DOM_WITH_CONTENT_TYPE_PROMPT"])(get_dom_with_content_type)

        # Register click_element skill for execution by user_proxy_agent
        self.user_proxy_agent.register_for_execution()(click_element)
        # Register click_element skill for LLM by assistant agent
        #self.agent.register_for_llm(description=LLM_PROMPTS["CLICK_PROMPT_ACCESSIBILITY"])(click_element)
        self.agent.register_for_llm(description=LLM_PROMPTS["CLICK_PROMPT"])(click_element)

        # Register geturl skill for execution by user_proxy_agent
        self.user_proxy_agent.register_for_execution()(geturl)
        # Register geturl skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["GET_URL_PROMPT"])(geturl)

        # Register bulk_enter_text skill for execution by user_proxy_agent
        self.user_proxy_agent.register_for_execution()(bulk_enter_text)
        # Register bulk_enter_text skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["BULK_ENTER_TEXT_PROMPT"])(bulk_enter_text)

        # Register entertext skill for execution by user_proxy_agent
        self.user_proxy_agent.register_for_execution()(entertext)
        # Register entertext skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["ENTER_TEXT_PROMPT"])(entertext)

        # Register reply function for printing messages
        self.user_proxy_agent.register_reply( # type: ignore
            [autogen.Agent, None],
            reply_func=print_message_from_user_proxy,
            config={"callback": None},
        )
        self.agent.register_reply( # type: ignore
            [autogen.Agent, None],
            reply_func=print_message_from_browser_agent,
            config={"callback": None},
        )
