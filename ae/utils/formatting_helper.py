
import json
import re
from typing import Any


def str_to_bool(s: str | bool) -> bool:
    """
    Convert a string representation of truth to True or False.

    Parameters:
    s (str | bool): The string to convert, or a boolean.

    Returns:
    bool: True if the string represents a truth value, False otherwise.
    """
    if isinstance(s, bool):
        return s
    return s.lower() in ['true', '1', 't', 'y', 'yes']

def str_to_json(s: str) -> dict[str, Any] | None:
    """
    Convert a string representation of a JSON object to a dictionary.

    Parameters:
    s (str): The string to convert.

    Returns:
    dict[str, Any] | None: The dictionary representation of the JSON object. If the parsing fails, returns None.
    """
    s_fixed = re.sub(r'(?<!\\)\n', '\\n', s) #escape newline characters as long as they are not already escaped

# Now you can safely load it using json.loads
    try:
        obj = json.loads(s_fixed)
        return obj
    except json.JSONDecodeError as e:
        return None

def is_terminating_message(message: str) -> bool:
    """
    Check if a message is a terminating message.

    Parameters:
    message (str): The message to check.

    Returns:
    bool: True if the message is a terminating message, False otherwise.
    """
    message_as_json = str_to_json(message)
    if message_as_json is None:
        if message.find('"terminate": "yes"') != -1:
            return True
        return False
    else:
        return message_as_json.get("terminate") == "yes"
