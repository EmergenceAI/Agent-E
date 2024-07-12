from datetime import datetime
from string import Template
import os

import autogen  # type: ignore
import agentops

from ae.core.memory.static_ltm import get_user_ltm
from ae.core.prompts import LLM_PROMPTS
from ae.core.skills.click_using_selector import click as click_element
from ae.core.skills.enter_text_using_selector import bulk_enter_text
from ae.core.skills.enter_text_using_selector import entertext
from ae.core.skills.get_dom_with_content_type import get_dom_with_content_type
from ae.core.skills.get_url import geturl
from ae.core.skills.open_url import openurl
from ae.core.skills.pdf_text_extractor import extract_text_from_pdf
from ae.core.skills.press_key_combination import press_key_combination

# Initialize AgentOps
agentops.init(os.getenv("AGENTOPS_API_KEY"))

@agentops.track_agent(name='BrowserNavAgent')
class BrowserNavAgent:
    @agentops.record_function('init_browser_nav_agent')
    def __init__(self, config_list, browser_nav_executor: autogen.UserProxyAgent):
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
        if user_ltm:
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

    @agentops.record_function('get_ltm')
    def __get_ltm(self):
        """
        Get the long term memory of the user.
        returns: str | None - The user LTM or None if not found.
        """
        return get_user_ltm()

    @agentops.record_function('register_skills')
    def __register_skills(self):
        """
        Register all the skills that the agent can perform.
        """
        skills = [
            (openurl, LLM_PROMPTS["OPEN_URL_PROMPT"]),
            (get_dom_with_content_type, LLM_PROMPTS["GET_DOM_WITH_CONTENT_TYPE_PROMPT"]),
            (click_element, LLM_PROMPTS["CLICK_PROMPT"]),
            (geturl, LLM_PROMPTS["GET_URL_PROMPT"]),
            (bulk_enter_text, LLM_PROMPTS["BULK_ENTER_TEXT_PROMPT"]),
            (entertext, LLM_PROMPTS["ENTER_TEXT_PROMPT"]),
            (press_key_combination, LLM_PROMPTS["PRESS_KEY_COMBINATION_PROMPT"]),
            (extract_text_from_pdf, LLM_PROMPTS["EXTRACT_TEXT_FROM_PDF_PROMPT"]),
        ]

        for skill, prompt in skills:
            self.__register_skill(skill, prompt)

    @agentops.record_function('register_skill')
    def __register_skill(self, skill, prompt):
        """
        Register a single skill for both the agent and the executor.
        """
        self.agent.register_for_llm(description=prompt)(skill)
        self.browser_nav_executor.register_for_execution()(skill)

# Example usage
if __name__ == "__main__":
    # This is just a placeholder. You'd typically create this with actual config and executor.
    config_list = [{}]
    browser_nav_executor = autogen.UserProxyAgent(name="executor")
    
    browser_nav_agent = BrowserNavAgent(config_list, browser_nav_executor)
    
    # Simulate some actions
    browser_nav_agent.agent.generate_reply("Open https://www.example.com")
    
    # End the AgentOps session
    agentops.end_session('Success')