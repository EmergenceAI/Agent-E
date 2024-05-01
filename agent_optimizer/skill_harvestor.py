import time
from ae.utils.anthropic_llm_helper import AnthropicLLMHelper
from ae.utils.logger import logger
from typing import Any
import json

from ae.core.prompts import LLM_PROMPTS
from ae.utils.gemini_llm_helper import GeminiLLMHelper
from agent_optimizer.skill_qualifier import does_harvested_skill_comply_with_rules


async def harvest_skills_from_chat_log(chat_logs_and_test_tasks: list[dict[str, Any]]):
    """
    Harvests skills from chat logs and test tasks.

    Args:
        chat_logs_and_test_tasks (list[dict[str, Any]]): A list of dictionaries containing chat logs and test tasks.

    Returns:
        dict[int, list[str]]: A dictionary where the key is the task_id and the value is a list of skills.
    """
    task_id_to_harvested_skills: dict[int, list[str]] = {}
    for chat_log_and_test_task in chat_logs_and_test_tasks:
        #add start and end time for the harvesting process
        start_time = time.time()
        chat_log = chat_log_and_test_task["chat_log"]
        test_result = chat_log_and_test_task["test_result"]
        logger.info(f"Processing chat log for task_id: {test_result['task_id']}")
        harvested_skills_raw =  await __prompt_llm_to_harvest_skills(json.dumps(chat_log), test_result["last_url"])
        #print("Harvested skills:\n", harvested_skills_raw)
        
        if not __were_there_skills_harvested(harvested_skills_raw):
            logger.info(f"No skills were harvested for task_id: {test_result['task_id']}")
            continue
        
        harvested_skills = await __cleanup_harvested_raw_skills(harvested_skills_raw)
        harvested_skills_final: list[str] = []
        for skill in harvested_skills:
            if not does_harvested_skill_comply_with_rules(skill):
                logger.info(f"Harvested skill for task_id {test_result['task_id']} does not comply with the rules. Skipping it. Here is the skill:\n{skill}")
            else:
                harvested_skills_final.append(skill)
                
        print(f"Cleaned up harvested skills count: {len(harvested_skills_final)} for task id: {test_result['task_id']}.")
        task_id_to_harvested_skills[test_result["task_id"]] = harvested_skills_final
        logger.info(f"Harvested skills for task_id {test_result['task_id']} took {time.time() - start_time} seconds.")
        
    return task_id_to_harvested_skills
        #STOPPED HERE. Need to register the function and do the same test with it to see if it will pass or not. 
        # The pass must have less steps than the original chat log and the new skill should be used. (maybe we should add this as an attribute of the chat log or the general entry that has test results and chat log)
        # otherwise it could be that it passed but without using the skill, as in we need to ensure that the chat results of the new test have the new skill in it

def __were_there_skills_harvested(harvested_skills_raw: str) -> bool:
    """
    Determines if skills were harvested.

    Args:
        harvested_skills_raw (str): The harvested raw skills.

    Returns:
        bool: True if skills were harvested, False otherwise.
    """
    if harvested_skills_raw and "NO NEW SKILLS" not in harvested_skills_raw:
        return True
    
    return False
    

async def __cleanup_harvested_raw_skills(harvested_tasks_raw: str) -> list[str]:
    """
    Cleans up the harvested raw skills.

    Args:
        harvested_tasks_raw (str): The harvested raw skills.

    Returns:
        str: The cleaned up harvested raw skills.
    """
    """"
    Given the embedded python code, extract from it the python function and their appropriate imports. If there are interdependencies between the functions then they should be considered one unit. Respond back with a json array of objects where each entry should have:
        - code: the actual code without dependencies
        - dependency functions: The functions that that the key code components depend on if any. These must be functions that are implemented in this string I am providing
        - imports: Any imports that are needed for the code in the helper functions or the main code
    """
    
    llm_helper = GeminiLLMHelper()
    response = await llm_helper.get_chat_completion_response_async(
        system_msg=LLM_PROMPTS["HARVESTED_SKILLS_CLEANUP_PROMPT"],
        user_msgs=[
            f"Here is the raw text that should contain python code:\n{harvested_tasks_raw}\n"
        ]
        , temperature=0, max_tokens=4000)
    try:
        if not response:
            logger.error(f"The LLM response for cleanup raw skills string was empty.\nRaw Skills String:\n{harvested_tasks_raw}")
            return []
        if response.strip().endswith("```"):
            response = response.strip()[:-3]
        cleaned_harvested_skills = json.loads(response)
        if cleaned_harvested_skills and len(cleaned_harvested_skills) > 0:
            harvest_skills = __assemble_skills_code(cleaned_harvested_skills)
            #logger.info(f"Harvested skills: {harvest_skills}")
            return harvest_skills
    except json.JSONDecodeError as e:
        logger.error(f"The LLM response for cleanup raw skills string was not in proper JSON format. Error: {e}.\nLLM Response:\n{response}")
    
    return []
    
    

def __assemble_skills_code(cleaned_harvested_skills: list[dict[str, list[str]]]) -> list[str]:
    """
    Assembles the skills code.

    Args:
        cleaned_harvested_skills (list[dict[str, list[str]]]): The cleaned harvested skills. Each entry should have: code and imports. Both should be lists of strings.

    Returns:
        list[str]: The assembled skills code. Each entry represents a skill.
    """
    harvest_skills: list[str] = []
    for skill in cleaned_harvested_skills:
        harvest_skill = '\n'.join(skill['imports']) + '\n' + '\n\n'.join(skill['code'])
        harvest_skills.append(harvest_skill)
        
    return harvest_skills



def __get_existing_skills_docs() -> str:
    #TODO: replace this with code that will read all the skills in the skills dir and return function signatures and docstrings
    with open("agent_optimizer/available_skills_docs.txt", "r") as file:
        skills_docs = file.read()
        return skills_docs

def __get_existing_skills_import_statements() -> str:
    #TODO: replace this with a way to get all the skills imports from the skills dir
    with open("agent_optimizer/available_skills_imports.txt", "r") as file:
        skills_imports = file.read()
        return skills_imports
        
async def __prompt_llm_to_harvest_skills(chat_log: str, last_url: str) -> str:
    #llm_helper = GeminiLLMHelper()
    llm_helper = AnthropicLLMHelper()
    response = await llm_helper.get_chat_completion_response_async(
        system_msg=LLM_PROMPTS["SKILLS_HARVESTING_PROMPT"],
        user_msgs=[
            f"Here are the existing skills definitions and documentation:\n{__get_existing_skills_docs()}\n",
            f"Here is how to import existing skills:\n{__get_existing_skills_import_statements()}\n",
            f"Here is final URL reached:\n{last_url}\n",
            f"Here is the chat log:\n{chat_log}\n"
        ]
        , temperature=0, max_tokens=4000)
    return response