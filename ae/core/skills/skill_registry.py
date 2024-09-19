# skill_registry.py
from collections.abc import Callable
from typing import Any

# Define the type of the functions that will be registered as skills
SkillType = Callable[..., Any]

# Global registry to store private skill functions and their metadata
skill_registry: list[dict[str, Any]] = []

def skill(description: str, name: str|None = None) -> Callable[[SkillType], SkillType]:
    """
    Decorator for registering private skills.

    Parameters:
    - description: A string describing the skill's function.
    - name: Optional name to register the skill with. If not provided, the function's name will be used.

    Returns:
    - A decorator function that registers the skill in the global registry.
    """
    def decorator(func: SkillType) -> SkillType:
        skill_registry.append({
            "name": name if name else func.__name__,  # Use provided name or fallback to function name
            "func": func,
            "description": description
        })
        return func
    return decorator
