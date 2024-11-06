def prompt__validate_action(task_action: str) -> str:
    return f"""# Task
You are an RPA bot that navigates digital UIs like a human. Your job is to validate that a certain action was successfully taken.

# Action
The action that was supposed to be taken was: "{task_action}"

# Question

The first screenshot shows the digital UI BEFORE the action was supposedly taken.
The second screenshot shows the digital UI AFTER the action was supposedly taken.

Given the change between the screenshots, was the action successfully taken? Be lenient and assume that the action was taken if the UI is "close enough" to the expected UI.

Answer in the JSON format:
{{
    "rationale": <rationale>,
    "was_taken": <true/false>
}}

Answer:"""


def prompt__validate_task__intro(task_descrip: str) -> str:
    return f"""# Task
Your job is to decide whether the workflow was successfully completed, as depicted by the following sequence of screenshots.

# Workflow

The workflow is: "{task_descrip}"

# User Interface

The workflow was executed within the web application shown in the screenshots.

# Workflow Demonstration

You are given the following sequence of screenshots which were sourced from a demonstration of the workflow.
The screenshots are presented in chronological order.

Here are the screenshots of the workflow:"""


def prompt__validate_task__close() -> str:
    return """
# Instructions

Given what you observe in the previous sequence of screenshots, was the workflow successfully completed?
If the workflow is asking a question, consider it completed successfully if you could deduce the answer to the question by viewing the screenshots.
If the workflow was completed successfully, then set `was_completed` to `true`

Provide your answer as a JSON dictionary with the following format:
{
    "rationale": <rationale>,
    "was_completed": <true/false>
}

Please write your JSON below:
"""


def prompt__validate_VQA_task__close() -> str:
    return """
# Instructions

Given what you observe in the previous sequence of screenshots, was the workflow successfully completed?
To determine this, derive few visual questions from the task description that upon answering will help decide if the workflow was successfully completed.
If the workflow is asking a question, consider it completed successfully if you could deduce the answer to the question by viewing the screenshots.
If the workflow was completed successfully, then set `was_completed` to `true`.
Also, provide the visual questions and their answers as part of the response.

Provide your answer as a JSON dictionary with the following format:
{
    "visual_questions": <list of visual questions and their answers>,
    "rationale": <rationale>,
    "was_completed": <true/false>
}

Please write your JSON below:
"""
