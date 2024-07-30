
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

