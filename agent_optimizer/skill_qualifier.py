def does_harvested_skill_comply_with_rules(harvested_skill: str) -> bool:
    """
    Determines if a harvested skill complies with the rules.

    Args:
        harvested_skill (str): The harvested skill.

    Returns:
        bool: True if the harvested skill complies with the rules, False otherwise.
    """
    if not harvested_skill:
        return False
    if "mmid" in harvested_skill:
        return False
    if "get_dom_with_content_type" in harvested_skill:
        return False
    return True