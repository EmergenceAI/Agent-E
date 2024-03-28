from typing import Annotated

from ae.core.playwright_manager import PlaywrightManager
from ae.utils.logger import logger


async def geturl() -> Annotated[str, "Returns the full URL of the current active web site/page."]:
    """
    Returns the full URL of the current page

    Parameters:

    Returns:
    - Full URL the browser's active page.
    """

    logger.info("Executing Get URL Command")
    try:
        # Create and use the PlaywrightManager
        browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
        page = await browser_manager.get_current_page()

        if not page:
            raise ValueError('No active page found. OpenURL command opens a new page.')

        # Get the URL of the current page
        url = page.url
        logger.debug("Returning URL: "+url)
        await browser_manager.notify_user("Grabbed the URL of the current page.")
        return url
    except Exception as e:
        raise ValueError('No active page found. OpenURL command opens a new page.') from e
