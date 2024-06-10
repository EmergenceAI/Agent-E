"""Implements helper functions to assist evaluation cases where other evaluators are not suitable."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from nltk.tokenize import word_tokenize  # type: ignore
from openai import OpenAI

load_dotenv()
client = OpenAI()


def llm_fuzzy_match(pred: str, reference: str, question: str) -> float:
    """
    Evaluates if a predicted answer matches a reference answer semantically, considering the context of a question.

    This function simulates a grading scenario, understanding that a student's answer may use different wording or phrasing from the reference answer. It uses GPT-4-turbo model to assess semantic equivalence.

    Parameters:
        pred (str): The student's predicted answer.
        reference (str): The reference answer to compare against.
        question (str): The question related to the answers.

    Returns:
        float: Returns 1.0 if the predicted answer is semantically equivalent to the reference, otherwise 0.0.
    """
    messages: list[dict[str, Any]] = []
    # construct the question to ask
    message = "Help a teacher to grade the answer of a student given a question. Keep in mind that the student may use different phrasing or wording to answer the question. The goal is to evaluate whether the answer is semantically equivalent to the reference answer.\n"
    message += f"question: {question}\n"
    message += f"reference answer: {reference}\n"
    message += "all the string 'N/A' that you see is a special sequence that means 'not achievable'\n"
    message += f"student answer: {pred}\n"
    message += "Conclude the judgement by correct/incorrect/partially correct."
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": message},
    ]

    response = generate_from_openai_chat_completion(
        model="gpt-4-turbo-preview",
        messages=messages,
        temperature=0,
        max_tokens=768,
        top_p=1.0,
        context_length=0,
    ).lower()
    if "partially correct" in response or "incorrect" in response:
        return 0.0
    else:
        assert "correct" in response
        return 1.0


def llm_ua_match(pred: str, reference: str, question: str) -> float:
    """
    Evaluates the alignment between a reported reason for a task being unachievable and the actual reason.

    This function reviews both the actual and reported reasons for a task's unachievability within the context of the task.
    It assesses if the reported reason is implicitly or explicitly in line with the actual reason, using GPT-turbo model.

    Parameters:
        pred (str): The reported unachievable reason by an individual.
        reference (str): The actual reason why the task is unachievable.
        question (str): The task in question.

    Returns:
        float: Returns 1.0 if the reported reason aligns with the actual reason, otherwise 0.0.
    """
    messages: list[dict[str, Any]] = []
    # construct the question to ask
    message = ""
    message += f"task: {question}\n"
    message += f"actual unachievable reason: {reference}\n"
    message += f"reported unachievable reason: {pred}\n"
    message += (
        "The task described above is inherently unachievable due to the reason specified under 'actual unachievable reason'. "
        "An individual previously attempted this task and was unable to complete it. They provided a reason for their failure, "
        "which is listed under 'reported unachievable reason'. Your role is to review both the actual and reported reasons. "
        "Determine if the reported reason aligns with the actual reason, even if implicitly. "
        "If the stated reason is in line with the actual reason, respond with 'same'. Otherwise, respond with 'different'."
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": message},
    ]

    response = generate_from_openai_chat_completion(
        model="gpt-4-turbo-preview",
        messages=messages,
        temperature=0,
        max_tokens=768,
        top_p=1.0,
        context_length=0,
    ).lower()
    if "different" in response:
        return 0.0
    else:
        assert "same" in response
        return 1.0



def generate_from_openai_chat_completion(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
    context_length: int,
    stop_token: str | None = None,
) -> str:
    """
    Generates a response from OpenAI's chat completions based on a conversation constructed from a list of messages.

    This function makes a call to the OpenAI API using specified parameters to control the generation.
    It requires an API key to be set in the environment variables.

    Parameters:
        messages (list[dict[str, str]]): A list of messages to construct the conversation context.
        model (str): The model name to use for generating the completion.
        temperature (float): Sampling temperature for generation.
        max_tokens (int): Maximum number of tokens to generate.
        top_p (float): Nucleus sampling parameter controlling the size of the probability mass to sample from.
        context_length (int): The maximum number of tokens from `messages` to use for context.
        stop_token (str, optional): A token at which to stop generating further tokens.

    Returns:
        str: The generated response as a string.

    Raises:
        ValueError: If the 'OPENAI_API_KEY' environment variable is not set.
    """
    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError(
            "OPENAI_API_KEY environment variable must be set when using OpenAI API."
        )
    client.api_key = os.environ["OPENAI_API_KEY"]
    client.organization = os.environ.get("OPENAI_ORGANIZATION", "")

    response = client.chat.completions.create(
        model=model,
        messages=messages, # type: ignore
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        n=1,
        stop=[stop_token] if stop_token else None,
    )
    answer: str = response.choices[0].message.content # type: ignore
    return answer

def clean_answer(answer: str) -> str:
    """Cleans and preprocesses the answer string for evaluation.

    Parameters:
        answer (str): The answer string to clean.

    Returns:
        str: The cleaned and lowercased answer string.
    """
    answer = answer.strip().strip('"').strip("'").lower()
    return answer

def evaluate_exact_match(ref: str, pred: str) -> float:
    """Evaluates if the predicted answer exactly matches the reference answer.

    Parameters:
        ref (str): The reference answer.
        pred (str): The predicted answer.

    Returns:
        float: 1.0 if the answers match exactly, otherwise 0.0.
    """
    return float(clean_answer(pred) == clean_answer(ref))

def evaluate_must_include(ref: str, pred: str, tokenize: bool = False) -> float:
    """Checks if the predicted answer includes all phrases from the reference answer.

    Parameters:
        ref (str): The reference answer containing phrases that must be included.
        pred (str): The predicted answer to be evaluated.
        tokenize (bool, optional): Tokenizes the answers before evaluation if True. Default is False.

    Returns:
        float: 1.0 if all phrases are included, otherwise 0.0.
    """
    clean_ref = clean_answer(ref)
    clean_pred = clean_answer(pred)
    if tokenize and len(clean_ref) == 1:
        return float(clean_ref in word_tokenize(clean_pred))
    else:
        return float(clean_ref in clean_pred)

def evaluate_fuzzy_match(ref: str, pred: str, intent: str) -> float:
    """Evaluates if the predicted answer is semantically similar to the reference answer.

    Uses a large language model to assess similarity based on the intent of the question.

    Parameters:
        ref (str): The reference answer.
        pred (str): The predicted answer.
        intent (str): The intent or context of the question.

    Returns:
        float: 1.0 if the answers are considered semantically similar, otherwise 0.0.
    """
    return llm_fuzzy_match(pred, ref, intent)

def evaluate_ua_match(ref: str, pred: str, intent: str) -> float:
    """Evaluates if the predicted reason for a task being unachievable matches the reference reason.

    Parameters:
        ref (str): The reference reason why the task is unachievable.
        pred (str): The predicted reason reported by the model.
        intent (str): The intent or context of the task.

    Returns:
        float: 1.0 if the reasons match, otherwise 0.0.
    """
    return llm_ua_match(pred, ref, intent)


def load_config(config_file: Path | str) -> list[dict[str, Any]]:
    """Load the confiufiguration for the test cases

    Args:
        config_file (Path | str): Path to the config file

    Returns:
        list[dict[str, Any]]: All the test cases in the config file
    """
    with open(config_file, "r") as f:  # noqa: UP015
        configs = json.load(f)
    return configs

def task_config_validator(task_config: dict[str, Any]) -> bool:
    # Access the attributes
    command = task_config.get('intent')

    if not command:
        raise ValueError("Intent is missing in the task config file. Without it the task cannot be run.")

    return True

def get_formatted_current_timestamp(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get the current timestamp in the specified format.

    Args:
        format (str, optional): The format of the timestamp. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: The current timestamp in the specified format.
    """
    # Get the current time
    current_time = datetime.now()

    # Format the timestamp as a human-readable string
    timestamp_str = current_time.strftime(format)
    return timestamp_str
