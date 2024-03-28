import asyncio

from playwright.async_api import Page

from ae.utils.logger import logger


async def wait_for_non_loading_dom_state(page: Page, max_wait_millis: int):
    max_wait_seconds = max_wait_millis / 1000
    end_time = asyncio.get_event_loop().time() + max_wait_seconds
    while asyncio.get_event_loop().time() < end_time:
        dom_state = await page.evaluate("document.readyState")
        if dom_state != "loading":
            logger.debug(f"DOM state is not 'loading': {dom_state}")
            break  # Exit the loop if the DOM state is not 'loading'

        await asyncio.sleep(0.05)
