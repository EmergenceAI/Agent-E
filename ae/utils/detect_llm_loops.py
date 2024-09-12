from typing import Any

from ae.utils.logger import logger


def is_agent_stuck_in_loop(messages: list[dict[str, Any]]) -> bool:
    """
    Detects loops in the agent's responses by iterating over the last N responses.

    Parameters
    ----------
    messages : list[dict[str, Any]]
        A list of dictionaries representing the agent's messages.

    Returns
    -------
    bool
        True if a loop is detected, False otherwise.
    """
    number_of_turns_to_check_for_loops: int = 6
    number_of_rounds_to_check_for_loops: int = number_of_turns_to_check_for_loops // 2 #integer division since we are checking for pairs of messages and can't have fractions
    # Detect any loops by checking the last number_of_rounds_to_check_for_loops tool responses and their corresponding tool calls
    if len(messages) > number_of_turns_to_check_for_loops:
        last_six_items = messages[-number_of_turns_to_check_for_loops:]
        logger.debug(f"More than {number_of_turns_to_check_for_loops} messages in the conversation. Checking for loops..")
        # Filter items by role
        tool_calls = [item for item in last_six_items if item.get("role") == "assistant"]

        # Check if function attributes are the same for tool items
        if tool_calls:
            tool_functions = [item.get("tool_calls", [{}])[0].get("function") for item in tool_calls]
            logger.debug(f"Last {number_of_rounds_to_check_for_loops} tool calls: {tool_functions}")
            if all(func == tool_functions[0] for func in tool_functions):
                logger.debug(f"Last {number_of_rounds_to_check_for_loops} tool calls are identical. Checking Tool responses..")
                # Check if content attributes are the same for assistant items
                tool_responses = [item for item in last_six_items if item.get("role") == "tool"]

                if tool_responses:
                    assistant_contents = [item.get("content") for item in tool_responses]
                    logger.debug(f"Last N tool responses: {assistant_contents}")
                    if all(content == assistant_contents[0] for content in assistant_contents):
                        logger.debug(f"Last {number_of_rounds_to_check_for_loops} tool responses are identical. Terminating")
                        logger.info("Terminating browser executor since a loop was detected...")
                        return True

    return False
