from typing import Annotated

from ae.core.playwright_manager import PlaywrightManager


async def geturl() -> Annotated[str, "Returns the full URL of the current active web site/page."]:
    """
    Returns the full URL of the current page

    Parameters:

    Returns:
    - Full URL the browser's active page.
    """


    try:
        # Create and use the PlaywrightManager
        browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
        page = await browser_manager.get_current_page()

        if not page:
            raise ValueError('No active page found. OpenURL command opens a new page.')

        await page.wait_for_load_state("domcontentloaded")

        # Get the URL of the current page
        try:
            title = await page.title()
            current_url = page.url
            if len(current_url) >250:
                current_url = current_url[:250] + "..."
            return f"Current Page: {current_url}, Title: {title}" # type: ignore
        except:  # noqa: E722
            current_url = page.url
            return f"Current Page: {current_url}"

    except Exception as e:
        raise ValueError('No active page found. OpenURL command opens a new page.') from e

