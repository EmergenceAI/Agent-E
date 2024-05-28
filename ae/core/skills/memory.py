from typing import Annotated
from ae.core.memory.static_ltm import get_user_ltm, save_user_ltm
from ae.core.playwright_manager import PlaywrightManager

async def add_to_memory(msg:str) -> Annotated[str, "Save any information that you may need later in this term memory. This could be useful for saving things to do, saving information for personalisation, or even saving information you may need in future for efficiency purposes E.g. Remember to call John at 5pm, This user likes Tesla company and considered buying shares, The user enrollment form is available in <url> etc."]:

    """
    Add a text to the short term memory.

    Parameters: msg (str): The text to be saved in the memory.

    Returns:
    - Total number of memories saved in the short term memory.
    """

    try:
        # Append the memory to the user_preferences.txt file
        save_user_ltm(msg)
        browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
        await browser_manager.notify_user(f"Saved to memory: {msg}")
        return f"Memory saved: {msg}" 

    except Exception as e:
        raise ValueError('Encountered an error while storing memory') from e


async def get_memory() -> Annotated[str|None, "Returns all the memories stored."]:
    """
    Returns all the memories available.

    Returns:
    - A text containing all the memories stored in the short term memory.
    """
    try: 
        memories=get_user_ltm()
        browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
        await browser_manager.notify_user(f"Retried all memories: {memories}")
        return memories
    except Exception as e:
        raise ValueError('Encountered an error while retrieving memory') from e
