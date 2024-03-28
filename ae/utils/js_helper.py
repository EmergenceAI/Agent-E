import json


def escape_js_message(message: str) -> str:
    """
    Escape a message for use in JavaScript code.

    Args:
        message (str): The message to escape.

    Returns:
        str: The escaped message.
    """
    return json.dumps(message)
