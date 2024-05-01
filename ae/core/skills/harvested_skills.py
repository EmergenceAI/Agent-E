#Task id: 0
import asyncio
from typing import Annotated
from ae.core.skills.click_using_selector import click as click_element
from ae.core.skills.enter_text_and_click import enter_text_and_click
from ae.core.skills.get_url import geturl
from ae.core.skills.open_url import openurl

async def search_amazon_and_sort_by_best_seller(search_term: Annotated[str, "The search term to use on Amazon"]) -> str:
    """
    Searches for a product on Amazon and sorts the results by best seller rank.
    
    Parameters:
    - search_term: The search term to use on Amazon
    
    Returns:
    - A message indicating the search was performed and results sorted by best seller, along with the final URL.
    """
    await openurl("https://www.amazon.com")
    await enter_text_and_click("[id='twotabsearchtextbox']", search_term, "[id='nav-search-submit-button']")
    await click_element("[value='exact-aware-popularity-rank']")
    url = await geturl()
    return f"The search for \"{search_term}\" on Amazon has been successfully performed and sorted by best seller. Final URL: {url}"


#Task id: 1
from typing import Annotated
from ae.core.skills.click_using_selector import click as click_element
from ae.core.skills.enter_text_and_click import enter_text_and_click
from ae.core.skills.get_url import geturl
from ae.core.skills.open_url import openurl
async def search_amazon_and_sort_by_price_desc(search_term: Annotated[str, "The search term to use on Amazon."]) -> str:

    """
    Searches for a product on Amazon and sorts the results by price descending (highest price first).

    Parameters:
    - search_term: The search term to use on Amazon.
    

    Returns:

    - The URL of the Amazon search results page with the results sorted by price descending.

    """

    await openurl("https://www.amazon.com")

    await enter_text_and_click("[id='twotabsearchtextbox']", search_term, "[id='nav-search-submit-button']")

    await click_element("[value='price-desc-rank']")

    return await geturl()


#Task id: 2
from ae.core.skills.click_using_selector import click as click_element
from ae.core.skills.open_url import openurl
async def navigate_to_espn_soccer() -> str:
    """
    Navigates to the soccer section on the ESPN website.

    Returns:
    - A message indicating the success or failure of the navigation.
    """
    await openurl("https://www.espn.com/")
    result = await click_element("[name='&lpos=sitenavdefault+sitenav_soccer']")
    await asyncio.sleep(1)
    current_utl = await geturl()
    if "clicked" in result:
        return f"Successfully navigated to the soccer section on ESPN. Current URL: {current_utl}"
    else:
        return "Failed to navigate to the soccer section on ESPN. " + result + ". Current URL: {current_utl}"


#Task id: 8
from ae.core.skills.click_using_selector import click as click_element
from ae.core.skills.open_url import openurl
async def navigate_to_mit_alumni_website() -> str:
    """
    Navigates to the MIT Alumni website from the MIT homepage.

    Returns:
    - A message indicating the success or failure of the navigation.
    """
    await openurl("https://www.mit.edu")
    result = await click_element("[href='/alumni']")
    
    if "clicked" in result:
        return "Successfully navigated to the MIT Alumni website."
    else:
        return "Failed to navigate to the MIT Alumni website. " + result


#Task id: 14
from ae.core.skills.click_using_selector import click as click_element
async def put_youtube_video_in_fullscreen() -> str:
    """
    Puts the currently playing YouTube video into fullscreen mode.

    Returns:
    - A message indicating the success or failure of putting the video in fullscreen mode.
    """
    fullscreen_button_selector = "button.ytp-fullscreen-button"
    
    try:
        result = await click_element(fullscreen_button_selector)
        return f"YouTube video put in fullscreen mode. {result}"
    except Exception as e:
        return f"Failed to put YouTube video in fullscreen mode. Error: {str(e)}"



#Task id: 22
from ae.core.skills.click_using_selector import click as click_element
from ae.core.skills.get_url import geturl
async def filter_jira_issues_by_done(
    filter_button_selector: Annotated[str, "The selector for the filter button to open filter options."] = "[aria-label='Switch filter']",
    done_filter_option_selector: Annotated[str, "The selector for the 'Done issues' filter option."] = "a[role='radio']"
) -> str:
    """
    Filters Jira issues by "Done" status on a Jira project issues page.

    Parameters:
    - filter_button_selector: The selector for the filter button to open filter options. Defaults to "[aria-label='Switch filter']".
    - done_filter_option_selector: The selector for the "Done issues" filter option. Defaults to "a[role='radio']".

    Returns:
    - A message indicating the filter has been set to show "Done issues" and the URL of the filtered page.
    """
    # Click the filter button to open filter options
    await click_element(filter_button_selector)
    
    # Click the "Done issues" filter option
    await click_element(done_filter_option_selector)

    # Get the URL of the filtered page
    filtered_url = await geturl()

    return f"The filter has been successfully set to show \"Done issues\" on the Jira project page. Filtered URL: {filtered_url}"