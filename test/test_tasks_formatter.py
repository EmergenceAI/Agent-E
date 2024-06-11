import json


# read the test configuration file, copy what is in task_id to task_alias and make task_id have an incremental numeric value, then save the file back to the same location
def format_test_config_file(test_config_file: str):
    with open(test_config_file, "r") as file:
        tasks = json.load(file)
    for i, task in enumerate(tasks):
        if "task_alias" in task:
            continue

        task["task_alias"] = task["task_id"]
        task["task_id"] = i
        tasks[i] = task
    with open(test_config_file, "w") as file:
        json.dump(tasks, file, indent=4)

def add_task_index_to_test_config_file(test_config_file: str):
    with open(test_config_file, "r") as file:
        tasks = json.load(file)
    for i, task in enumerate(tasks):
        task["task_index"] = i
        tasks[i] = task
    with open(test_config_file, "w") as file:
        json.dump(tasks, file, indent=4)
format_test_config_file("test/tasks/webvoyager_test.json")
add_task_index_to_test_config_file("test/tasks/webvoyager_test.json")
