import asyncio
import inspect
from typing import Annotated

from playwright.async_api import Page  # type: ignore

from ae.core.playwright_manager import PlaywrightManager
from ae.utils.dom_mutation_observer import subscribe  # type: ignore
from ae.utils.dom_mutation_observer import unsubscribe  # type: ignore
from ae.utils.logger import logger
from ae.utils.ui_messagetype import MessageType


async def press_key_combination(key_combination: Annotated[str, "The key to press, e.g., Enter, PageDown etc"]) -> str:
    """
    Presses a key combination on the current active page managed by PlaywrightManager.

    This function simulates the pressing of a key or a combination of keys on the current active web page.
    The `key_combination` should be a string that represents the keys to be pressed, separated by '+' if it's a combination.
    For example, 'Control+C' to copy or 'Alt+F4' to close a window on Windows.

    Parameters:
    - key_combination (Annotated[str, "The key combination to press, e.g., 'Control+C'."]): The key combination to press, represented as a string. For combinations, use '+' as a separator.

    Raises:
    - ValueError: If no active page is found.

    Returns:
    str: status of the operation expressed as a string
    """

    logger.info(f"Executing press_key_combination with key combo: {key_combination}")
    # Create and use the PlaywrightManager
    browser_manager = PlaywrightManager()
    page = await browser_manager.get_current_page()

    if page is None: # type: ignore
        raise ValueError('No active page found. OpenURL command opens a new page.')

    # Split the key combination if it's a combination of keys
    keys = key_combination.split('+')

    dom_changes_detected=None
    def detect_dom_changes(changes:str): # type: ignore
        nonlocal dom_changes_detected
        dom_changes_detected = changes # type: ignore

    subscribe(detect_dom_changes)
    # If it's a combination, hold down the modifier keys
    for key in keys[:-1]:  # All keys except the last one are considered modifier keys
        await page.keyboard.down(key)

    # Press the last key in the combination
    await page.keyboard.press(keys[-1])

    # Release the modifier keys
    for key in keys[:-1]:
        await page.keyboard.up(key)
    await asyncio.sleep(0.1) # sleep for 100ms to allow the mutation observer to detect changes
    unsubscribe(detect_dom_changes)

    if dom_changes_detected:
        return f"Key {key_combination} executed successfully.\n As a consequence of this action, new elements have appeared in view:{dom_changes_detected}. This means that the action is not yet executed and needs further interaction. Get all_fields DOM to complete the interaction."

    await browser_manager.notify_user(f"Key {key_combination} executed successfully", message_type=MessageType.ACTION)
    return f"Key {key_combination} executed successfully"


async def do_press_key_combination(browser_manager: PlaywrightManager, page: Page, key_combination: str) -> bool:
    """
    Presses a key combination on the provided page.

    This function simulates the pressing of a key or a combination of keys on a web page.
    The `key_combination` should be a string that represents the keys to be pressed, separated by '+' if it's a combination.
    For example, 'Control+C' to copy or 'Alt+F4' to close a window on Windows.

    Parameters:
    - browser_manager (PlaywrightManager): The PlaywrightManager instance.
    - page (Page): The Playwright page instance.
    - key_combination (str): The key combination to press, represented as a string. For combinations, use '+' as a separator.

    Returns:
    bool: True if success and False if failed
    """

    logger.info(f"Executing press_key_combination with key combo: {key_combination}")
    try:
        function_name = inspect.currentframe().f_code.co_name # type: ignore
        await browser_manager.take_screenshots(f"{function_name}_start", page)
        # Split the key combination if it's a combination of keys
        keys = key_combination.split('+')

        # If it's a combination, hold down the modifier keys
        for key in keys[:-1]:  # All keys except the last one are considered modifier keys
            await page.keyboard.down(key)

        # Press the last key in the combination
        await page.keyboard.press(keys[-1])

        # Release the modifier keys
        for key in keys[:-1]:
            await page.keyboard.up(key)

    except Exception as e:
        logger.error(f"Error executing press_key_combination \"{key_combination}\": {e}")
        return False

    await browser_manager.take_screenshots(f"{function_name}_end", page)

    return True

