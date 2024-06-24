from typing import Annotated
from ae.utils.logger import logger

import os
from openai import OpenAI
from ae.core.prompts import LLM_PROMPTS

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
    user_prompt = f"Given a the webtask task {intent}, do you believe {lastest_plan} is sufficient in completing the afformentioned task? Please answer yes or no. If the plan is not valid, please provide feedback on which portions are not valid and why."
    OpenAI.api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("AUTOGEN_MODEL_NAME")
    client = OpenAI()
    feedback = client.chat.completions.create(
        model=model_name,
          messages=[
            {"role": "system", "content": LLM_PROMPTS["VERFICATION_AGENT"]},
            {"role": "user", "content": user_prompt},
        ]
    )
    #feedback = feedback.choices[0].message.content #Extract message from chat completion object
    # feedback = "Your plan sucks. Please try again."
    #feedback = "Your plan is valid."
    print(f"*** Feedback is: {feedback}\n")
    return feedback