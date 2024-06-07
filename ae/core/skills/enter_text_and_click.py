from typing import Annotated

from ae.core.playwright_manager import PlaywrightManager
from ae.core.skills.click_using_selector import do_click
from ae.core.skills.enter_text_using_selector import do_entertext
from ae.utils.logger import logger
from ae.utils.dom_mutation_observer import subscribe # type: ignore
from ae.utils.dom_mutation_observer import unsubscribe # type: ignore

import asyncio 

async def enter_text_and_click(
    text_selector: Annotated[str, "The properly formatted DOM selector query, for example [mmid='1234'], where the text will be entered. Use mmid attribute."],
    text_to_enter: Annotated[str, "The text that will be entered into the element specified by text_selector."],
    click_selector: Annotated[str, "The properly formatted DOM selector query, for example [mmid='1234'], for the element that will be clicked after text entry."],
    wait_before_click_execution: Annotated[float, "Optional wait time in seconds before executing the click.", float] = 0.0
) -> Annotated[str, "A message indicating success or failure of the text entry and click."]:
    """
    Enters text into an element and then clicks on another element.

    Parameters:
    - text_selector: The selector for the element to enter text into. It should be a properly formatted DOM selector query, for example [mmid='1234'], where the text will be entered. Use the mmid attribute.
    - text_to_enter: The text to enter into the element specified by text_selector.
    - click_selector: The selector for the element to click. It should be a properly formatted DOM selector query, for example [mmid='1234'].
    - wait_before_click_execution: Optional wait time in seconds before executing the click action. Default is 0.0.

    Returns:
    - A message indicating the success or failure of the text entry and click.

    Raises:
    - ValueError: If no active page is found. The OpenURL command opens a new page.

    Example usage:
    ```
    await enter_text_and_click("[mmid='1234']", "Hello, World!", "[mmid='5678']", wait_before_click_execution=1.5)
    ```
    """
    logger.info(f"Entering text '{text_to_enter}' into element with selector '{text_selector}' and then clicking element with selector '{click_selector}'.")

    # Initialize PlaywrightManager and get the active browser page
    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    page = await browser_manager.get_current_page()
    if page is None: # type: ignore
        logger.error("No active page found")
        raise ValueError('No active page found. OpenURL command opens a new page.')

    await browser_manager.highlight_element(text_selector, True)
    dom_changes_detected=None
    
    def detect_dom_changes(changes:str): # type: ignore
        nonlocal dom_changes_detected
        dom_changes_detected = changes # type: ignore

    subscribe(detect_dom_changes)

    text_entry_result = await do_entertext(page, text_selector, text_to_enter, use_keyboard_fill=True)

    await browser_manager.notify_user(text_entry_result["summary_message"])
    if not text_entry_result["summary_message"].startswith("Success"):
        return(f"Failed to enter text '{text_to_enter}' into element with selector '{text_selector}'. Check that the selctor is valid.")
    await asyncio.sleep(0.1) # sleep for 100ms to allow the mutation observer to detect changes
    unsubscribe(detect_dom_changes)
    result = text_entry_result

    if dom_changes_detected:
        result["summary_message"] = f"{result['summary_message']}. \n As a consequence of this action, new elements have appeared in view: {dom_changes_detected}.  Get all_fields DOM to interact with it. Note that i have not clicked on the element you suggested. Use a click_on_selector skill to initiate a click."
        return result["summary_message"]
    
    await browser_manager.highlight_element(click_selector, True)
    subscribe(detect_dom_changes)
    do_click_result = await do_click(page, click_selector, wait_before_click_execution)
    result["detailed_message"] = f' {do_click_result["detailed_message"]}'
    await asyncio.sleep(0.1) # sleep for 100ms to allow the mutation observer to detect changes
    unsubscribe(detect_dom_changes)
    await browser_manager.notify_user(do_click_result["summary_message"])
    if dom_changes_detected:
        return f"{result['summary_message']}. \n As a consequence of this action, new elements have appeared in view:{dom_changes_detected}. Get all_fields DOM to interact with it."
    return result["detailed_message"]
