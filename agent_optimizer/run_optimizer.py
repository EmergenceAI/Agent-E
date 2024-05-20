import ast
import asyncio
import json
import os
import re
import time
from typing import Any

from ae.config import PROJECT_TEST_ROOT
from ae.utils.logger import logger

from agent_optimizer.chat_log_analyzer import abbreviate_long_messages
from agent_optimizer.chat_log_analyzer import is_chat_log_candidate_for_optimization
from agent_optimizer.chat_log_analyzer import load_chat_log_from_file
from agent_optimizer.skill_harvestor import harvest_skills_from_chat_log

test_logs_dir = os.path.join(PROJECT_TEST_ROOT, 'logs')
test_results_dir = os.path.join(PROJECT_TEST_ROOT, 'results')
test_tasks_file = os.path.join(PROJECT_TEST_ROOT, 'tasks', 'test.json')
task_id_extraction_pattern = re.compile(r"execution_logs_(\d+)\.json")


def retrieve_test_results(test_results_file: str, only_passing_tests: bool=True):
    test_results_file_full_path = os.path.join(test_results_dir, test_results_file)
    logger.info(f"Retrieving test results from file: {test_results_file_full_path}")

    with open(test_results_file_full_path, 'r') as file:
        test_results: list[dict[str, Any]] = json.load(file)
        if only_passing_tests:
            test_results = filter(lambda test: int(test["score"]) == 1, test_results) # type: ignore
    task_id_to_test_results: dict[int, dict[str, Any]] = {}
    for test in test_results:
        task_id = int(test["task_id"])
        task_id_to_test_results[task_id] = test

    return task_id_to_test_results


def retrieve_chat_logs() -> dict[int, dict[str, Any]]:
    """
    Retrieves chat logs from a directory and returns a dictionary where the key is the task_id and the value is a dictionary containing task_id and chat_log.

    Returns:
        dict[int, dict[str, Any]]: A dictionary where the key is the task_id and the value is a dictionary containing task_id and chat_log.
    """
    task_id_to_chat_logs: dict[int, dict[str, Any]] = {}
    for file in os.listdir(test_logs_dir):
        print(f"Processing chat log file: {file}")
        if file.startswith("execution_logs") and file.endswith(".json"): # only consider the chat logs
            task_id = -1 #task_id is embedded in the file name
            task_id_match = task_id_extraction_pattern.match(file)
            if task_id_match:
                task_id = int(task_id_match.group(1))
                print(f"Found task_id: {task_id}")
            #load the content of the chat log
            chat_log = load_chat_log_from_file(os.path.join(test_logs_dir, file))
            if is_chat_log_candidate_for_optimization(chat_log):
                chat_log = abbreviate_long_messages(chat_log)
                task_id_to_chat_logs[task_id] = {"task_id": task_id, "chat_log": chat_log}
            else:
                logger.info(f"Chat log {file} is not a candidate for optimization. This can be due to the number of assistant turns.")
        else:
            logger.info(f"Skipping file {file} because it does not match expected pattern 'execution_logs_<task_id>.json'.")

    return task_id_to_chat_logs


def add_test_results_to_chat_logs(test_results: dict[int, dict[str, Any]], task_id_to_chat_logs: dict[int, dict[str, Any]]):
    """
    Add test results to the chat logs.
    """
    chat_logs_and_test_results: list[dict[str, Any]] = []
    for task_id, chat_log_entry in task_id_to_chat_logs.items():
        test_result = test_results.get(task_id)
        if test_result:
            chat_logs_and_test_results.append({"task_id": task_id, "chat_log": chat_log_entry["chat_log"], "test_result": test_result})
        else:
            logger.warning(f'Test result not found for task_id {task_id}. It may have been filtered out because it did not pass.')

    return chat_logs_and_test_results


def add_test_cards_to_chat_logs(test_tasks_file: str, task_id_to_chat_logs: dict[int, dict[str, Any]]):
    """
    Add test cards to the chat logs.
    """
    chat_logs_and_test_tasks: list[dict[str, Any]] = []
    with open(test_tasks_file, 'r') as file:
        test_tasks: list[dict[str, Any]] = json.load(file)
        for test in test_tasks:
            task_id = int(test.get("task_id", "-1"))
            chat_log_entry = task_id_to_chat_logs.get(task_id)
            if chat_log_entry:
                chat_logs_and_test_tasks.append({"chat_log": chat_log_entry["chat_log"], "test_task": test})
            else:
                print(f'Test task not found for task_id {test.get("task_id")}.')

    return chat_logs_and_test_tasks

def convert_harvested_skills_to_function(harvested_skills: list[str]):
    """
    Convert harvested skills to a function.
    """
    pass



def convert_harvested_skill_to_function(harvested_skill: str) -> dict[str, Any]:
    """
    Analyzes and executes a string of Python code to determine the main function and retrieve all defined functions.

    The main function is defined as the one that calls other functions but is not called by any other.

    Args:
        harvested_skill (str): The string containing the Python code with function definitions.

    Returns:
        dict[str, Any]: A dictionary containing:
            - "main_function_name": The name of the main function (str) or None if not determinable.
            - "functions": A dictionary where keys are function names and values are the function objects.
    """
    # Parse the code string into an AST
    tree = ast.parse(harvested_skill)

    # Initialize a dictionary to keep track of which functions call other functions
    function_calls = {node.name: [] for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

    # If there's only one function, we can immediately set it as the main function
    if len(function_calls) == 1:
        main_function_name = next(iter(function_calls))
    else:
        # Walk the tree to find all function definitions and their calls
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # For each function definition, check its body for function calls
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        # If a function call is found, add it to the dictionary
                        function_calls[node.name].append(child.func.id) # type: ignore

        # Find the main function
        all_called_functions = set()  # type: ignore
        for calls in function_calls.values(): # type: ignore
            for func in calls: # type: ignore
                all_called_functions.add(func)  # type: ignore

        # Identify candidate main functions
        main_function_candidates = []
        for func in function_calls:
            if func not in all_called_functions:
                main_function_candidates.append(func) # type: ignore

        # Determine the main function name if there is one candidate
        main_function_name = main_function_candidates[0] if len(main_function_candidates) == 1 else None  # type: ignore

    # Create a local namespace dictionary to execute the code
    local_namespace: dict[str, Any] = {}
    exec(harvested_skill, local_namespace)

    # Extract only the functions from the local namespace
    functions = {name: obj for name, obj in local_namespace.items() if callable(obj)}

    return {
        "main_function_name": main_function_name,
        "functions": functions
    }

def run_tests_with_harvested_skills(harvested_skills: list[str], test_task_config: dict[str, Any]):
    """
    Run tests with harvested skills.
    """
    if not harvested_skills:
        logger.info(f"No harvested skills to run tests with, no need to rerun tests for task {test_task_config['task_id']}.")
        return
    #TODO: figure out how to create autogen wrapper and add the harvested skills to it, then run the test returning back the test results and chat logs
    pass

def did_test_pass_with_harvested_skills(test_results: dict[int, dict[str, Any]], chat_logs_and_test_tasks: list[dict[str, Any]]):
    """
    Determine if the test passed and the harvested skills were used.
    """
    pass
    #TODO: determine that the test passed then figure out how to get the name of the harvested skills (maybe that should be passed in)

async def main():
    start_time = time.time()
    task_id_to_test_results = retrieve_test_results("test_results_all_tests_with_new_skills_output2.json")
    task_id_to_chat_logs = retrieve_chat_logs()
    chat_logs_and_test_tasks = add_test_results_to_chat_logs(task_id_to_test_results, task_id_to_chat_logs)

    #print(json.dumps(chat_logs_and_test_tasks, indent=2))
    harvested_skills = await harvest_skills_from_chat_log(chat_logs_and_test_tasks)
    print(">>> harvested_skills\n", json.dumps(harvested_skills, indent=2))

    #STOPPED HERE. Need to register the function and do the same test with it to see if it will pass or not.
    # tests_processor.execute_single_task should now allow for the passing of autogen_wrapper. This is where the harvested skill needs to be registered.
        # The pass must have less steps than the original chat log and the new skill should be used. (maybe we should add this as an attribute of the chat log or the general entry that has test results and chat log)
        # otherwise it could be that it passed but without using the skill, as in we need to ensure that the chat results of the new test have the new skill in it
    #This function convert_harvested_skill_to_function needs to be used to get the functions and the main function. The thinking is maybe just create a dir for temp 
    #harvested skills and dump the string containing harvested skill in it. Then we need to somehow import the new file and register that function with the autogen_wrapper
    #Not sure how this will work with importing the function that may have dependancy on some imports .
    #One idea is to change the autogen wrapper code to look for some file called harvested functions and add them if a flag is passed?
    #Finally since we have the name of the main function we need to search the chatlog (as a string for "name": "main_function_name here". Alternatively, we can go through the chat log 
    # look for "role": "assistant" and then check the called functions. But the regex match should be sufficient.

    logger.info(f"Total time taken for skills harvesting: {time.time() - start_time} seconds.")

if __name__ == "__main__":
    asyncio.run(main())
