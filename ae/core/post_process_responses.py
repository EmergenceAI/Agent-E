from typing import Any

import autogen  # type: ignore
import asyncio
from ae.core.playwright_manager import PlaywrightManager
from ae.utils.logger import logger


def final_reply_callback_user_proxy(recipient: autogen.ConversableAgent, messages: list[dict[str, Any]], sender: autogen.Agent, config: dict[str, Any]):
    """
    Callback function that is called each time the user proxy agent receives a message.
    It picks the last message from the list of messages and checks if it contains the termination signal.
    If the termination signal is found, it extracts the final response and outputs it.

    Args:
        recipient (autogen.ConversableAgent): The recipient of the message.
        messages (Optional[list[dict[str, Any]]]): The list of messages received by the agent.
        sender (Optional[autogen.Agent]): The sender of the message.
        config (Optional[Any]): Additional configuration parameters.

    Returns:
        Tuple[bool, None]: A tuple indicating whether the processing should stop and the response to be sent.
    """
    global last_agent_response
    last_message = messages[-1]
    logger.debug(f"Post Process Message (User Proxy):{last_message}")
    if last_message.get('content') and "##TERMINATE##" in last_message['content']:
        last_agent_response = last_message['content'].replace("##TERMINATE##", "").strip()
        if last_agent_response:
            logger.debug("*****Final Reply*****")
            logger.debug(f"Final Response: {last_agent_response}")
            logger.debug("*********************")
            return True, None

    return False, None


def final_reply_callback_planner_agent(message:str, level:str = "plan"): # type: ignore 
            browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(browser_manager.notify_user(message, message_type=level))
            return False, None  # required to ensure the agent communication flow continues
