import time
from typing import Any
import asyncio
from ae.config import PROJECT_TEST_ROOT
from ae.utils.logger import logger
import os
import re
import json
from agent_optimizer.chat_log_analyzer import load_chat_log_from_file, abbreviate_long_messages, is_chat_log_candidate_for_optimization
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


async def main():
    start_time = time.time()
    task_id_to_test_results = retrieve_test_results("test_results_all_tests_with_new_skills_output2.json")
    task_id_to_chat_logs = retrieve_chat_logs()
    chat_logs_and_test_tasks = add_test_results_to_chat_logs(task_id_to_test_results, task_id_to_chat_logs)
    
    #print(json.dumps(chat_logs_and_test_tasks, indent=2))
    harvested_skills = await harvest_skills_from_chat_log(chat_logs_and_test_tasks)
    print(">>> harvested_skills\n", json.dumps(harvested_skills, indent=2))
    logger.info(f"Total time taken for skills harvesting: {time.time() - start_time} seconds.")

if __name__ == "__main__":
    asyncio.run(main())
