import time
from typing import Annotated

from playwright.async_api import Page

from ae.core.playwright_manager import PlaywrightManager
from ae.core.skills.click_using_selector import do_click
from ae.utils.logger import logger


async def press_key_combination(key_combination: Annotated[str, "The key combination to press using '+' as a separator, e.g., 'Control+C', Enter, PageDown etc"]) -> str:
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
    start_time = time.time()
    # Create and use the PlaywrightManager
    browser_manager = PlaywrightManager()
    page = await browser_manager.get_current_page()

    if page is None: # type: ignore
        raise ValueError('No active page found. OpenURL command opens a new page.')

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

    print(f"Operation completed in {time.time() - start_time} seconds.")
    return f"Key combination {key_combination} executed successfully"

async def press_enter_key(selector: Annotated[str, """The properly formed query selector string to identify the element to press enter key in.
                                              When \"mmid\" attribute is present, use it for the query selector."""]) -> Annotated[str, "A message indicating success or failure."]:
    logger.info(f"Executing press_enter_key with selector: \"{selector}\"")
    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    page = await browser_manager.get_current_page()

    if page is None: # type: ignore
        raise ValueError('No active page found. OpenURL command opens a new page.')

    await do_click(page, selector, wait_before_execution=0.0)
    result = await do_press_key_combination(page, 'Enter')

    if result:
        return f"Enter key pressed in field with selector: {selector}"
    else:
        return f"Failed to press Enter key in field with selector: {selector}"


async def do_press_key_combination(page: Page, key_combination: str) -> bool:
    """
    Presses a key combination on the provided page.

    This function simulates the pressing of a key or a combination of keys on a web page.
    The `key_combination` should be a string that represents the keys to be pressed, separated by '+' if it's a combination.
    For example, 'Control+C' to copy or 'Alt+F4' to close a window on Windows.

    Parameters:
    - page (Page): The Playwright page instance.
    - key_combination (str): The key combination to press, represented as a string. For combinations, use '+' as a separator.

    Returns:
    bool: True if success and False if failed
    """

    logger.info(f"Executing press_key_combination with key combo: {key_combination}")
    try:
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
    return True
