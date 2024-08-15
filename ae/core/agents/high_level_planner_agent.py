from datetime import datetime
from string import Template
from typing import Any

import autogen  # type: ignore
from autogen import ConversableAgent  # type: ignore

from ae.core.memory.static_ltm import get_user_ltm
from ae.core.post_process_responses import final_reply_callback_planner_agent as print_message_as_planner  # type: ignore
from ae.core.prompts import LLM_PROMPTS
from ae.core.skills.get_user_input import get_user_input
from ae.utils.logger import logger


class PlannerAgent:
    def __init__(self, model_config_list, llm_config_params: dict[str, Any], system_prompt: str|None, user_proxy_agent:ConversableAgent): # type: ignore
        """
        Initialize the PlannerAgent and store the AssistantAgent instance
        as an instance attribute for external access.

        Parameters:
        - model_config_list: A list of configuration parameters required for AssistantAgent.
        - llm_config_params: A dictionary of configuration parameters for the LLM.
        - system_prompt: The system prompt to be used for this agent or the default will be used if not provided.
        - user_proxy_agent: An instance of the UserProxyAgent class.
        """
        user_ltm = self.__get_ltm()
        system_message = LLM_PROMPTS["PLANNER_AGENT_PROMPT"]

        if system_prompt:
            system_message = system_prompt
            logger.info("Using custom system prompt for PlannerAgent")

        if user_ltm: #add the user LTM to the system prompt if it exists
            user_ltm = "\n" + user_ltm
            system_message = Template(system_message).substitute(basic_user_information=user_ltm)
        system_message = system_message + "\n" + f"Today's date is {datetime.now().strftime('%d %B %Y')}"
        logger.info(f"Planner agent using model: {model_config_list[0]['model']}")

        self.agent = autogen.AssistantAgent(
            name="planner_agent",
            system_message=system_message,
            llm_config={
                "config_list": model_config_list,
                **llm_config_params #unpack all the name value pairs in llm_config_params as is
            },
        )

        # Register get_user_input skill for LLM by assistant agent
        self.agent.register_for_llm(description=LLM_PROMPTS["GET_USER_INPUT_PROMPT"])(get_user_input)
        # Register get_user_input skill for execution by user_proxy_agent
        user_proxy_agent.register_for_execution()(get_user_input)

        self.agent.register_reply( # type: ignore
            [autogen.AssistantAgent, None],
            reply_func=print_message_as_planner,
            config={"callback": None},
            ignore_async_in_sync_chat=True
        )

    def __get_ltm(self):
        """
        Get the the long term memory of the user.
        returns: str | None - The user LTM or None if not found.
        """
        return get_user_ltm()

