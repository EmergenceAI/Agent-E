from typing import Annotated
from ae.core.memory.static_ltm import get_user_ltm
from ae.core.playwright_manager import PlaywrightManager
from ae.utils.dom_mutation_observer import subscribe # type: ignore
from ae.utils.dom_mutation_observer import unsubscribe # type: ignore

async def hover_on_element(selector: Annotated[str, "The properly formed query selector string to identify the element for hover action. When \"mmid\" attribute is present, use it for the query selector."]):

    """
    Hover on an element identified by the given query selector string.
    Hover can be used to trigger events popup, tooltip, etc.
    """

    # Append the memory to the user_preferences.txt file
    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    page = await browser_manager.get_current_page()
    if page is None: # type: ignore
            raise ValueError('No active page found. OpenURL command opens a new page.')
    dom_changes_detected=None
    def detect_dom_changes(changes): # type: ignore
        nonlocal dom_changes_detected
        dom_changes_detected = changes # type: ignore
    
    subscribe(detect_dom_changes)
    await page.hover(selector)
    unsubscribe(detect_dom_changes)
    if dom_changes_detected:
        return f"Hovered on element {selector} successfully.\n As a consequence of this action, new elements have appeared in view:{dom_changes_detected}. This could be a drop down or a tooltop."

    return f"Hovered on element {selector} successfully. No changes were observed in the DOM"

