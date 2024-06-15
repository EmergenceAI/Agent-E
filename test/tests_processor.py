import asyncio
import json
import os
import time
from test.evaluators import evaluator_router
from test.test_utils import get_formatted_current_timestamp
from test.test_utils import load_config
from test.test_utils import task_config_validator
from typing import Any

import ae.core.playwright_manager as browserManager
import nltk  # type: ignore
from ae.config import PROJECT_TEST_ROOT
from ae.core.autogen_wrapper import AutogenWrapper
from ae.core.playwright_manager import PlaywrightManager
from ae.utils.logger import logger
from ae.utils.response_parser import parse_response
from autogen.agentchat.chat import ChatResult  # type: ignore
from playwright.async_api import Page
from tabulate import tabulate
from termcolor import colored

nltk.download('punkt') # type: ignore

TEST_TASKS = os.path.join(PROJECT_TEST_ROOT, 'tasks')
TEST_LOGS = os.path.join(PROJECT_TEST_ROOT, 'logs')
TEST_RESULTS = os.path.join(PROJECT_TEST_ROOT, 'results')

last_agent_response = ""

def check_top_level_test_folders():
    if not os.path.exists(TEST_LOGS):
        os.makedirs(TEST_LOGS)
        logger.info(f"Created log folder at: {TEST_LOGS}")

    if not os.path.exists(TEST_RESULTS):
        os.makedirs(TEST_RESULTS)
        logger.info(f"Created scores folder at: {TEST_RESULTS}")

def create_test_results_id(test_results_id: str|None, test_file: str) -> str:
    prefix = "test_results_for_"
    if test_results_id:
        return f"{prefix}{test_results_id}"
    test_file_base = os.path.basename(test_file)
    test_file_name = os.path.splitext(test_file_base)[0]

    return f"{prefix}{test_file_name}"

def create_task_log_folders(task_id: str, test_results_id: str):
    task_log_dir = os.path.join(TEST_LOGS, f"{test_results_id}", f'logs_for_task_{task_id}')
    task_screenshots_dir = os.path.join(task_log_dir, 'snapshots')
    if not os.path.exists(task_log_dir):
        os.makedirs(task_log_dir)
        logger.info(f"Created log dir for task {task_id} at: {task_log_dir}")
    if not os.path.exists(task_screenshots_dir):
        os.makedirs(task_screenshots_dir)
        logger.info(f"Created screenshots dir for task {task_id} at: {task_screenshots_dir}")

    return {"task_log_folder": task_log_dir, "task_screenshots_folder": task_screenshots_dir}


def create_results_dir(test_file: str, test_results_id: str|None) -> str:
    results_dir = ""
    if test_results_id:
        results_dir = os.path.join(TEST_RESULTS, f"results_for_{test_results_id}")
    else:
        test_file_base = os.path.basename(test_file)
        test_file_name = os.path.splitext(test_file_base)[0]
        results_dir = os.path.join(TEST_RESULTS, f"results_for_test_file_{test_file_name}")

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        logger.info(f"Created results directory: {results_dir}")

    return results_dir


def dump_log(task_id: str, messages_str_keys: dict[str, str], logs_dir: str):
    file_name = os.path.join(logs_dir, f'execution_logs_{task_id}.json')
    with open(file_name, 'w',  encoding='utf-8') as f:
            json.dump(messages_str_keys, f, ensure_ascii=False, indent=4)


def save_test_results(test_results: list[dict[str, str | int | float | None]], test_results_id: str):
    file_name = os.path.join(TEST_RESULTS, f'test_results_{test_results_id}.json')
    with open(file_name, 'w',  encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=4)
    logger.info(f"Test results dumped to: {file_name}")


def save_individual_test_result(test_result: dict[str, str | int | float | None], results_dir: str):
    task_id = test_result["task_id"]
    file_name = os.path.join(results_dir, f'test_result_{task_id}.json')
    with open(file_name, 'w',  encoding='utf-8') as f:
        json.dump(test_result, f, ensure_ascii=False, indent=4)
    logger.info(f"Test result for task {task_id} dumped to: {file_name}")


def extract_last_response(messages: list[dict[str, Any]]) -> str:
    """Extract the last response message from chat history."""
    try:
        # Iterate over the messages in reverse order
        for message in reversed(messages):
            if message and 'content' in message:
                content=message.get('content', "")
                content_json = parse_response(content)
                final_answer = content_json.get('final_response', None)
                if final_answer:
                    return final_answer
        return ""
    except:
        logger.error("Error extracting last response from chat history.")
        return ""


def print_progress_bar(current: int, total: int, bar_length: int = 50) -> None:
    """
    Prints a progress bar to the console.

    Parameters:
    - current (int): The current progress of the task.
    - total (int): The total number of tasks to complete.
    - bar_length (int): The character length of the progress bar (default is 50).

    This function dynamically updates a single line in the console to reflect current progress.

    """
    percent = float(current) * 100 / total
    arrow = '-' * int(percent/100 * bar_length - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    print(f'\rProgress: [{arrow}{spaces}] {current}/{total} ({percent:.2f}%)', end='')

def determine_status_and_color(score: float) -> tuple[str, str]:
    """
    Determines the status and color for a test result based on the score.

    Parameters:
    - score (float): The score of the test task, indicating success (1), failure (0), or skip (-0.1).

    Returns:
    - tuple[str, str]: A tuple containing the status ('Pass', 'Fail', or 'Skip') and the corresponding color ('green', 'red', or 'yellow').

    """
    if score == 1:
        return 'Pass', 'green'
    elif score < 0:
        return 'Skip', 'yellow'
    else:
        return 'Fail', 'red'


def print_test_result(task_result: dict[str, str | int | float | None], index: int, total: int) -> None:
    """
    Prints the result of a single test task in a tabulated format.

    Parameters:
    - task_result (dict): A dictionary containing the task's evaluation results, including task ID, intent, score, and total command time.
    - index (int): The current index of the test in the sequence of all tests being run.
    - total (int): The total number of tests to be run.

    The function determines the test status (Pass/Fail) based on the 'score' key in task_result and prints the result with colored status.

    """
    status, color = determine_status_and_color(task_result['score']) # type: ignore

    cost = task_result.get("compute_cost", None)
    total_cost = None if cost is None else round(cost.get("cost", -1), 4)  # type: ignore
    total_tokens = None if cost is None else cost.get("total_tokens", -1)  # type: ignore
    result_table = [  # type: ignore
        ['Test Index', 'Task ID', 'Intent', 'Status', 'Time Taken (s)', 'Total Tokens', 'Total Cost ($)'],
        [index, task_result['task_id'], task_result['intent'], colored(status, color), round(task_result['tct'], 2), total_tokens, total_cost]  # type: ignore
    ]
    print('\n' + tabulate(result_table, headers='firstrow', tablefmt='grid')) # type: ignore

def get_command_exec_cost(command_exec_result: ChatResult):
    output: dict[str, Any] = {}
    try:
        cost = command_exec_result.cost # type: ignore
        usage: dict[str, Any] = None
        if "usage_including_cached_inference" in cost:
            usage: dict[str, Any] = cost["usage_including_cached_inference"]
        elif "usage_excluding_cached_inference" in cost:
            usage: dict[str, Any] = cost["usage_excluding_cached_inference"]
        else:
            raise ValueError("Cost not found in the command execution result.")
        print("Usage: ", usage)

        for key in usage.keys():
            if isinstance(usage[key], dict) and "prompt_tokens" in usage[key]:
                output["cost"] = usage[key]["cost"]
                output["prompt_tokens"] = usage[key]["prompt_tokens"]
                output["completion_tokens"] = usage[key]["completion_tokens"]
                output["total_tokens"] = usage[key]["total_tokens"]
    except Exception as e:
        logger.debug(f"Error getting command execution cost: {e}")
    return output


async def execute_single_task(task_config: dict[str, Any], browser_manager: PlaywrightManager, ag: AutogenWrapper, page: Page, logs_dir: str) -> dict[str, Any]:
    """
    Executes a single test task based on a specified task configuration and evaluates its performance.

    Parameters:
    - task_config (dict): The task configuration dictionary containing all necessary parameters for the task.
    - browser_manager (PlaywrightManager): The manager handling browser interactions, responsible for page navigation and control.
    - ag (AutogenWrapper): The automation generator wrapper that processes commands and interacts with the web page.
    - page (Page): The Playwright page object representing the browser tab where the task is executed.

    Returns:
    - dict: A dictionary containing the task's evaluation results, including task ID, intent, score, total command time (tct),
            the last statement from the chat agent, and the last URL accessed during the task.
    """
    command = ""
    start_url = None
    task_id = None

    start_ts = get_formatted_current_timestamp()

    task_config_validator(task_config)

    command: str = task_config.get('intent', "")
    task_id = task_config.get('task_id')
    task_index = task_config.get('task_index')
    start_url = task_config.get('start_url')
    logger.info(f"Intent: {command}, Task ID: {task_id}")

    if start_url:
        await page.goto(start_url, wait_until='load', timeout=30000)

    start_time = time.time()
    current_url = await browser_manager.get_current_url()
    command_exec_result = await ag.process_command(command, current_url)
    end_time = time.time()

    evaluator_result: dict[str, float | str] = {}
    last_agent_response: str = ""
    command_cost: dict[str, Any] = {}
    single_task_result: dict[str, Any] = {}
    try:
        single_task_result = {
            "task_id": task_id,
            "task_index": task_index,
            "start_url": start_url,
            "intent": str(command),
            "last_url": page.url,
            "tct": end_time - start_time,
            "start_ts": start_ts,
            "completion_ts": get_formatted_current_timestamp()
        }

        agent_name: str = "planner_agent" if ag.agents_map is not None and "planner_agent" in ag.agents_map else "browser_nav_agent"

        command_cost = get_command_exec_cost(command_exec_result) # type: ignore
        print(f"Command cost: {command_cost}")
        single_task_result["compute_cost"] = command_cost

        logger.info(f"Command \"{command}\" took: {round(end_time - start_time, 2)} seconds.")
        logger.info(f"Task {task_id} completed.")

        messages = ag.agents_map[agent_name].chat_messages # type: ignore
        messages_str_keys = {str(key): value for key, value in messages.items()} # type: ignore
        agent_key = list(messages.keys())[0] # type: ignore
        last_agent_response = extract_last_response(messages[agent_key]) # type: ignore

        dump_log(str(task_id), messages_str_keys, logs_dir)

        single_task_result["last_statement"] = last_agent_response


        evaluator = evaluator_router(task_config)
        cdp_session = await page.context.new_cdp_session(page)
        evaluator_result = await evaluator(
            task_config=task_config,
            page=page,
            client=cdp_session,
            answer=last_agent_response,
        )

        single_task_result["score"] = evaluator_result["score"]
        single_task_result["reason"] = evaluator_result["reason"]
    except Exception as e:
        logger.error(f"Error getting command cost: {e}")
        command_cost = {"cost": -1, "total_tokens": -1}
        single_task_result["compute_cost"] = command_cost
        single_task_result["error"] = str(e)

    return single_task_result


async def run_tests(ag: AutogenWrapper, browser_manager: PlaywrightManager, min_task_index: int, max_task_index: int,
               test_file: str="", test_results_id: str = "", wait_time_non_headless: int=5, take_screenshots: bool = False) -> list[dict[str, Any]]:
    """
    Runs a specified range of test tasks using Playwright for browser interactions and AutogenWrapper for task automation.
    It initializes necessary components, processes each task, handles exceptions, and compiles test results into a structured list.

    Parameters:
    - ag (AutogenWrapper): The AutoGen wrapper that processes commands.
    - browser_manager (PlaywrightManager): The manager handling browser interactions, responsible for page navigation and control.
    - min_task_index (int): The index of the first test task to execute (inclusive).
    - max_task_index (int): The index of the last test task to execute (non-inclusive).
    - test_file (str): Path to the file containing the test configurations. If not provided, defaults to a predetermined file path.
    - test_results_id (str): A unique identifier for the session of test results. Defaults to a timestamp if not provided.
    - wait_time_non_headless (int): Time to wait between tasks when running in non-headless mode, useful for live monitoring or debugging.
    - take_screenshots (bool): Whether to take screenshots during test execution. Defaults to False.

    Returns:
    - list[dict[str, Any]]: A list of dictionaries, each containing the results from executing a test task. Results include task ID, intent, score, total command time, etc.

    This function also manages logging and saving of test results, updates the progress bar to reflect test execution status, and prints a detailed summary report at the end of the testing session.
    """
    check_top_level_test_folders()

    if not test_file or test_file == "":
        test_file = os.path.join(TEST_TASKS, 'test.json')

    logger.info(f"Loading test configurations from: {test_file}")

    test_configurations = load_config(test_file)

    test_results_id = create_test_results_id(test_results_id, test_file)

    results_dir = create_results_dir(test_file, test_results_id)
    test_results: list[dict[str, str | int | float | None]] = []

    if not ag:
        ag = await AutogenWrapper.create()

    if not browser_manager:
        browser_manager = browserManager.PlaywrightManager(headless=False)
        await browser_manager.async_initialize()

    page=await browser_manager.get_current_page()
    test_results = []
    max_task_index = len(test_configurations) if not max_task_index else max_task_index
    total_tests = max_task_index - min_task_index

    for index, task_config in enumerate(test_configurations[min_task_index:max_task_index], start=min_task_index):
        task_id = str(task_config.get('task_id'))

        log_folders = create_task_log_folders(task_id, test_results_id)

        ag.set_chat_logs_dir(log_folders["task_log_folder"])

        browser_manager.set_take_screenshots(take_screenshots)
        if take_screenshots:
            browser_manager.set_screenshots_dir(log_folders["task_screenshots_folder"])

        print_progress_bar(index - min_task_index, total_tests)
        task_result = await execute_single_task(task_config, browser_manager, ag, page, log_folders["task_log_folder"])
        test_results.append(task_result)
        save_individual_test_result(task_result, results_dir)
        print_test_result(task_result, index + 1, total_tests)

        if not browser_manager.isheadless: # no need to wait if we are running headless
            await asyncio.sleep(wait_time_non_headless)  # give time for switching between tasks in case there is a human observer

        await browser_manager.take_screenshots("final", None)

        await browser_manager.close_except_specified_tab(page) # cleanup pages that are not the one we opened here

    print_progress_bar(total_tests, total_tests)  # Complete the progress bar
    print('\n\nAll tests completed.')

    # Aggregate and print individual test results
    print("\nDetailed Test Results:")
    detailed_results_table = [['Test Index', 'Task ID', 'Intent', 'Status', 'Time Taken (s)', 'Total Tokens', 'Total Cost ($)']]
    for idx, result in enumerate(test_results, 1):
        status, color = determine_status_and_color(result['score']) # type: ignore

        cost: str | int | float | None = result.get("compute_cost", None)
        total_cost = None if cost is None else round(cost.get("cost", -1), 4)  # type: ignore
        total_tokens = None if cost is None else cost.get("total_tokens", -1)  # type: ignore

        detailed_results_table.append([
            idx, result['task_id'], result['intent'], colored(status, color), round(result['tct'], 2), # type: ignore
            total_tokens, total_cost
        ])

    print(tabulate(detailed_results_table, headers='firstrow', tablefmt='grid'))

    # Summary report

    # Calculate aggregated cost and token totals for all tests that have compute cost
    total_cost = 0
    total_tokens = 0

    for result in test_results:
        compute_cost = result.get("compute_cost",0) # type: ignore
        if compute_cost is not None and isinstance(compute_cost, dict):
            total_cost += compute_cost.get("cost", 0) # type: ignore
            total_tokens += compute_cost.get("total_tokens", 0) # type: ignore

    passed_tests = []
    skipped_tests = []
    failed_tests = []
    for result in test_results:
        if result["score"] == 1:
            passed_tests.append(result) # type: ignore
        elif result["score"] < 0: # type: ignore
            skipped_tests.append(result) # type: ignore
        else:
            failed_tests.append(result) # type: ignore

    summary_table = [ # type: ignore
        ['Total Tests', 'Passed', 'Failed', 'Skipped', 'Average Time Taken (s)', 'Total Time Taken (s)', 'Total Tokens', 'Total Cost ($)'],
        [total_tests, len(passed_tests), len(failed_tests), len(skipped_tests),
        round(sum(test['tct'] for test in test_results) / total_tests, 2), # type: ignore
        round(sum(test['tct'] for test in test_results), 2),  # type: ignore
        total_tokens, total_cost]
    ]

    print('\nSummary Report:')
    print(tabulate(summary_table, headers='firstrow', tablefmt='grid')) # type: ignore

    return test_results
