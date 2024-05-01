from typing import Any
import json

def load_chat_log_from_file(file_path: str) -> list[dict[str, Any]]:
    """
    Loads a chat log from a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        list[dict[str,Any]]: The chat log.
    """
    with open(file_path, 'r') as file:
        chat_log = json.load(file)
        #only need the values of the chat_log dictionary because it normally has a key like: "<autogen.agentchat.user_proxy_agent.UserProxyAgent object at ...>"
        chat_log: list[dict[str, Any]] = list(chat_log.values())[0] # type: ignore
    return chat_log # type: ignore


def abbreviate_long_messages(chat_log: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Abbreviates long messages in a chat log. For now focused on removing HTML DOM content.

    Args:
        chat_log (list[dict[str,Any]]): The chat log to abbreviate.

    Returns:
        list[dict[str,Any]]: The chat log with long messages abbreviated.
    """
    for item in chat_log:
        if item.get("role") == "tool":
            content = item.get("content")
            if content and content.startswith('{\"role\": \"WebArea\"'):
                item["content"] = "HTML DOM content removed for brevity."
                
                if "tool_responses" in item:
                    for tool_response in item["tool_responses"]:
                        if tool_response.get("content"):
                            tool_response["content"] = "HTML DOM content removed for brevity."
    return chat_log


def is_chat_log_candidate_for_optimization(chat_log: list[dict[str, Any]]) -> bool:
    """
    Determines if a chat log is a candidate for optimization.

    Args:
        chat_log (list[dict[str,Any]]): The chat log to analyze.

    Returns:
        bool: True if the chat log is a candidate for optimization, False otherwise.
    """
    # Count the number of objects with "role": "assistant"
    assistant_turns_count = sum(1 for item in chat_log if item.get("role") == "assistant")
    
    #TODO: consider a rule for chats that have fetched the DOM text content, what is the value in optimizing those? Maybe breaking those chats down into smaller parts?
    #TODO: should we only optimize chat logs of successful tests? As in we need the test results to be shared too.
    
    return assistant_turns_count >= 3
