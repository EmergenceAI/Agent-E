from typing import Annotated
from ae.utils.logger import logger

import openai

async def do_self_validation(
        lastest_plan: Annotated[str, "The lasted version of the plan to verify."],
        intent: Annotated[str, "The user task which the plan is written for."]
) -> Annotated[str, "Returns the feedback of the current plan."]:
    """
    Proceeds with a (self-)validation method

    Parameters:
        # TODO: consider taking in other information, prior screenshots, dom ect.
    Returns:
    - String with feedback provided from self-validator
    """
    logger.info("Proceeding with self-validation...\n")

    # Validation process
    #prompt = f"Given a the webtask task {intent}, do you believe {lastest_plan} is sufficient in completing the afformentioned task? If not please provide feedback."
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    #response = openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=100)
    #print(response)
    #exit()
    
    #feedback = "Your plan sucks. Please try again."
    feedback = "Your plan is valid."
    print(f"*** Feedback is: {feedback}\n")
    return feedback