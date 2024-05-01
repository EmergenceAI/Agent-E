import argparse
import asyncio
import json
import os
import time
from test.evaluators import evaluator_router
from test.test_utils import load_config
from test.test_utils import task_config_validator
from typing import Any

import ae.core.playwright_manager as browserManager
import nltk  # type: ignore
from ae.config import PROJECT_TEST_ROOT
from ae.core.autogen_wrapper import AutogenWrapper
from ae.core.playwright_manager import PlaywrightManager
from ae.utils.logger import logger
from playwright.async_api import Page
from tabulate import tabulate
from termcolor import colored

nltk.download('punkt') # type: ignore

TEST_TASKS = os.path.join(PROJECT_TEST_ROOT, 'tasks')
TEST_LOGS = os.path.join(PROJECT_TEST_ROOT, 'logs')
TEST_RESULTS = os.path.join(PROJECT_TEST_ROOT, 'results')

last_agent_response = ""

def check_test_folders():
    if not os.path.exists(TEST_LOGS):
        os.makedirs(TEST_LOGS)
        logger.info(f"Created log folder at: {TEST_LOGS}")

    if not os.path.exists(TEST_RESULTS):
        os.makedirs(TEST_RESULTS)
        logger.info(f"Created scores folder at: {TEST_RESULTS}")


def dump_log(task_id: str, messages_str_keys: dict[str, str]):
    file_name = os.path.join(TEST_LOGS, f'execution_logs_{task_id}.json')
    with open(file_name, 'w',  encoding='utf-8') as f:
            json.dump(messages_str_keys, f, ensure_ascii=False, indent=4)


def save_test_results(test_results: list[dict[str, str | int | float | None]], test_results_id: str):
    file_name = os.path.join(TEST_RESULTS, f'test_results_{test_results_id}.json')
    with open(file_name, 'w',  encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=4)
    logger.info(f"Test results dumped to: {file_name}")


async def execute_test_task(index: int, task_config: dict[str, Any], browser_manager: PlaywrightManager, ag: AutogenWrapper, page: Page) -> dict[str, str | int | float | None]:
    """
    Executes a test task based on a specified task configuration and evaluates its performance.

    Parameters:
    - index (int): The index of the task to be executed, used to identify the task configuration file.
    - task_config (dict): The task configuration dictionary containing all th necessary parameters for the task.
    - browser_manager (PlaywrightManager): The manager handling browser interactions, responsible for page navigation and control.
    - ag (AutogenWrapper): The automation generator wrapper that processes commands and interacts with the web page.
    - page (Page): The Playwright page object representing the browser tab where the task is executed.

    Returns:
    - dict: A dictionary containing the task's evaluation results, including task ID, intent, score, total command time (tct),
            the last statement from the chat agent, and the last URL accessed during the task.

    """
    command = None
    start_url = None
    task_id = None
    try:
        task_config_validator(task_config)

        command = task_config.get('intent')
        task_id = task_config.get('task_id')
        start_url = task_config.get('start_url')
        logger.info(f"Intent: {command}, Task ID: {task_id}")

        if start_url:
            await page.goto(start_url, wait_until='load', timeout=30000)

        start_time = time.time()
        current_url = await browser_manager.get_current_url()
        await ag.process_command(command, current_url) # type: ignore
        end_time = time.time()

        logger.info(f"Command \"{command}\" took: {round(end_time - start_time, 2)} seconds.")
        logger.info(f"Task {task_id} completed.")

        messages = ag.agents_map["browser_nav_agent"].chat_messages # type: ignore
        messages_str_keys = {str(key): value for key, value in messages.items()} # type: ignore
        agent_key = list(messages.keys())[0] # type: ignore
        last_agent_response = extract_last_response(messages[agent_key]) # type: ignore

        dump_log(str(task_id), messages_str_keys) # type: ignore

        evaluator = evaluator_router(task_config)
        cdp_session = await page.context.new_cdp_session(page)
        score = await evaluator(
            task_config=task_config,
            page=page, # type: ignore
            client=cdp_session, # type: ignore
            answer=last_agent_response,
        )

        return {
            "task_id": task_id,
            "start_url": start_url,
            "intent": str(command),
            "score": score,
            "tct": end_time - start_time,
            "last_statement": last_agent_response,
            "last_url": page.url
        }
    except Exception as e:
        logger.error(f"Error executing task {task_id}: {e}")
        return {
            "task_id": task_id,
            "start_url": start_url,
            "intent": str(command),
            "score": -1,
            "tct": 0,
            "last_statement": None,
            "last_url": page.url,
            "error": str(e)
        }


def extract_last_response(messages: list[dict[str, Any]]) -> str:
    """Extract the last response message from chat history."""
    # Iterate over the messages in reverse order
    for message in reversed(messages):
        if '##TERMINATE##' in message.get('content', ''):
            return message['content'].replace("##TERMINATE##", "").strip()
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


def print_test_result(task_result: dict[str, str | int | float | None], index: int, total: int) -> None:
    """
    Prints the result of a single test task in a tabulated format.

    Parameters:
    - task_result (dict): A dictionary containing the task's evaluation results, including task ID, intent, score, and total command time.
    - index (int): The current index of the test in the sequence of all tests being run.
    - total (int): The total number of tests to be run.

    The function determines the test status (Pass/Fail) based on the 'score' key in task_result and prints the result with colored status.

    """
    status = 'Pass' if task_result['score'] == 1 else 'Fail'
    color = 'green' if status == 'Pass' else 'red'
    result_table = [ # type: ignore
        ['Test Index', 'Task ID', 'Intent', 'Status', 'Time Taken (s)'],
        [index, task_result['task_id'], task_result['intent'], colored(status, color), round(task_result['tct'], 2)] # type: ignore
    ]
    print('\n' + tabulate(result_table, headers='firstrow', tablefmt='grid')) # type: ignore

async def main(min_task_index: int, max_task_index: int, test_file: str="", test_results_id: str = "", wait_time_non_headless: int=5) -> None:
    """
    The main function to run the test suite with specified range of test tasks.

    This function initializes necessary components, iterates over test tasks within the specified range,
    executes them, and prints individual test results and a summary report at the end. It uses a progress bar
    to indicate the overall progress of the test suite.

    The range of test tasks to be executed can be specified via command line parameters. If not provided,
    default values are used.

    Parameters:
    - min_task_index (int): The index of the first test task to execute (inclusive).
                            Command line parameter: --min_task_index or -min. Default is 0.
    - max_task_index (int): The index of the last test task to execute (non-inclusive).
                            Command line parameter: --max_task_index or -max.
    - test_results_id (str): A unique identifier for the test results. If not provided, a timestamp is used.
    - wait_time_non_headless (int): The time to wait between test tasks when running in non-headless mode.

    """
    if not test_file or test_file == "":
        test_file = os.path.join(TEST_TASKS, 'test.json')

    logger.info(f"Loading test configurations from: {test_file}")

    test_configurations = load_config(test_file)

    if not test_results_id or test_results_id == "":
        test_results_id = str(int(time.time()))

    check_test_folders()
    test_results: list[dict[str, str | int | float | None]] = []

    ag = await AutogenWrapper.create()
    browser_manager = browserManager.PlaywrightManager(headless=False)
    await browser_manager.async_initialize()
    context = await browser_manager.get_browser_context()
    page = await context.new_page() # type: ignore

    test_results = []
    max_task_index = len(test_configurations) if not max_task_index else max_task_index
    total_tests = max_task_index - min_task_index

    for index, task_config in enumerate(test_configurations[min_task_index:max_task_index], start=min_task_index):
        print_progress_bar(index - min_task_index, total_tests)
        task_result = await execute_test_task(index, task_config, browser_manager, ag, page, agent_optimizer=None)
        test_results.append(task_result)
        save_test_results(test_results, test_results_id)
        print_test_result(task_result, index + 1, total_tests)
        await browser_manager.close_except_specified_tab(page) #cleanup pages that are not the one we opened here

        if not browser_manager.isheadless: #no need to wait if we are running headless
            await asyncio.sleep(wait_time_non_headless)  # give time for switching between tasks in case there is a human observer

    print_progress_bar(total_tests, total_tests)  # Complete the progress bar
    print('\n\nAll tests completed.')

    # Aggregate and print individual test results
    print("\nDetailed Test Results:")
    detailed_results_table = [['Test Index', 'Task ID', 'Intent', 'Status', 'Time Taken (s)']]
    for idx, result in enumerate(test_results, 1):
        status = 'Pass' if result['score'] == 1 else 'Fail'
        color = 'green' if status == 'Pass' else 'red'
        detailed_results_table.append([
            idx, result['task_id'], result['intent'], colored(status, color), round(result['tct'], 2) # type: ignore
        ])
    print(tabulate(detailed_results_table, headers='firstrow', tablefmt='grid'))

    # Summary report
    passed_tests = [result for result in test_results if result['score'] == 1]
    summary_table = [ # type: ignore
        ['Total Tests', 'Passed', 'Failed', 'Average Time Taken (s)', 'Total Time Taken (s)'],
        [total_tests, len(passed_tests), total_tests - len(passed_tests), round(sum(test['tct'] for test in test_results) / total_tests, 2), round(sum(test['tct'] for test in test_results), 2)] # type: ignore
    ]
    print('\nSummary Report:')
    print(tabulate(summary_table, headers='firstrow', tablefmt='grid')) # type: ignore

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Run test suite for specified range of test tasks.')

    # Add arguments
    parser.add_argument('-wait', '--wait_time_non_headless', type=int, default=10,
                        help='Time to wait between test tasks when running in non-headless mode (default: 10 seconds)')
    parser.add_argument('-min', '--min_task_index', type=int, default=0,
                        help='Minimum task index to start tests from (default: 0)')
    parser.add_argument('-max', '--max_task_index', type=int,
                        help='Maximum task index to end tests with, non-inclusive (default is all the tests in the file).')
    parser.add_argument('-id', '--test_results_id', type=str, default="",
                        help='A unique identifier for the test results. If not provided, a timestamp is used.')
    parser.add_argument('-config', '--test_config_file', type=str,
                        help='Path to the test configuration file. Default is "test/tasks/test.json" in the project root.')

    # Parse the command line arguments
    args = parser.parse_args()

    # Run the main function with the provided or default arguments
    asyncio.run(main(args.min_task_index, args.max_task_index, test_results_id=args.test_results_id, test_file=args.test_config_file))
