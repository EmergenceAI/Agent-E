from typing import Annotated
from typing import List  # noqa: UP035

from ae.core.playwright_manager import PlaywrightManager
from ae.utils.cli_helper import answer_questions_over_cli


async def get_user_input(questions: Annotated[List[str], "List of questions to ask the user each one represented as a string"] ) -> dict[str, str]:  # noqa: UP006
    """
    Asks the user a list of questions and returns the answers in a dictionary.

    Parameters:
    - questions: A list of questions to ask the user ["What is Username?", "What is your password?"].

    Returns:
    - Newline separated list of questions to ask the user
    """

    answers: dict[str, str] = {}
    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    if browser_manager.ui_manager:
        for question in questions:
            answers[question] = await browser_manager.prompt_user(f"Question: {question}")
    else:
        answers = await answer_questions_over_cli(questions)
    return answers
