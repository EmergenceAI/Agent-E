from string import Template

import autogen  # type: ignore
from typing import Union
from typing import Tuple, Optional
from typing import List, Dict
from ae.core.memory.static_ltm import get_user_ltm
from ae.core.prompts import LLM_PROMPTS
from autogen import Agent  
from autogen import OpenAIWrapper  

class VerificationAgent:
    def __init__(self, config_list): # type: ignore
        """
        Initialize the VerificationAgent and store the AssistantAgent instance
        as an instance attribute for external access.

        Parameters:
        - config_list: A list of configuration parameters required for AssistantAgent.
        - user_proxy_agent: An instance of the UserProxyAgent class.
        """

        user_ltm = self.__get_ltm()
        system_message = LLM_PROMPTS["PLANNER_AGENT_PROMPT"]
        print(f">>> Verifier system_message: {system_message}")
        if user_ltm: #add the user LTM to the system prompt if it exists
            user_ltm = "\n" + user_ltm
            system_message = Template(system_message).substitute(basic_user_information=user_ltm)

        self.agent = autogen.ConversableAgent(
            name="planner_agent",
            system_message=system_message,
            llm_config={
                "config_list": config_list,
                "cache_seed": 2,
                "temperature": 0.0
            },
        )
        self.agent.generate_oai_reply = self._generate_oai_reply # type: ignore


    def __get_ltm(self):
        """
        Get the the long term memory of the user.
        returns: str | None - The user LTM or None if not found.
        """
        return get_user_ltm()


    def _generate_oai_reply(self, # type: ignore
        messages: Optional[List[Dict]] = None, # type: ignore
        Header: Optional[Agent] = None, # type: ignore
        config: Optional[OpenAIWrapper] = None # type: ignore
    ) -> Tuple[bool, Union[str, Dict, None]] : # type: ignore

        print(f">>> generate_oai_reply: {messages}")
        print(f">>> Header: {Header}")
        return True, "Hello from PlannerAgent"