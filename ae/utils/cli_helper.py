import asyncio
from asyncio import Future


def async_input(prompt: str) -> Future: # type: ignore
    """
    Display a prompt to the user and wait for input in an asynchronous manner.

    Parameters:
    - prompt: The message to display to the user.

    Returns:
    - A Future object that will be fulfilled with the user's input.
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, input, prompt)


async def answer_questions_over_cli(questions: list[str]) -> dict[str, str]:
    """
    Asks a question over the command line and awaits the user's response.

    Parameters:
    - questions: A list of questions to ask the user, e.g., ["What is your favorite site?", "What do you want to search for?"].

    Returns:
    - A dictionary where each key is a question and each value is the user's response.
    """
    answers: dict[str, str] = {}
    print("*********************************")
    for question in questions:
        answers[question] = await async_input("Question: "+str(question)+" : ")
    print("*********************************")
    return answers
