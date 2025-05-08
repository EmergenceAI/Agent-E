from typing import Annotated, Union
import asyncio

from ae.core.skills.skill_registry import skill


@skill(description="Pauses execution for a specified number of seconds.")
async def wait(duration: Annotated[Union[int, float], "Number of seconds to wait"]) -> Annotated[str, "Result of the waiting operation"]:
    """
    Pauses execution for a specified number of seconds.

    Parameters:
    - duration: The number of seconds to wait (can be integer or float).

    Returns:
    - A message indicating the wait has completed.

    Raises:
    - ValueError: If the duration is negative or not a valid number.
    """
    try:
        # Convert to float to handle both int and float inputs
        seconds = float(duration)
        
        # Check for negative values
        if seconds < 0:
            raise ValueError("Duration cannot be negative.")
        
        # Perform the waiting operation
        await asyncio.sleep(seconds)
        
        # Return completion message
        if seconds == 1:
            return f"Waited for {seconds} second."
        else:
            return f"Waited for {seconds} seconds."
            
    except ValueError as e:
        # Specific error for negative values or parsing errors
        if "negative" in str(e):
            raise ValueError("Duration cannot be negative.") from e
        else:
            raise ValueError("Invalid duration. Please provide a valid number of seconds.") from e
    except Exception as e:
        # Generic error handler
        raise ValueError(f"Error while waiting: {str(e)}") from e 