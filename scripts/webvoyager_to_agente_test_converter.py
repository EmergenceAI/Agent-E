import json
from typing import Any

'''
The script reads the Webvoyager dataset, combines it with WebVoyager reference answer
to a format Agent-E can understand and run.
All evaluations are manual.
Run the code as follows:
python WebVoyager_converter.py
The script expects WebVoyager_data.jsonl and WebVoyager_reference_answer.json (from webvoyager repo) to be in the same directory.
The script will generate a file named webvoyager_test.json in the tasks directory. This file is compatible with Agent-E evaluation framework.
'''


def get_reference_answer(domain:str, id:int, reference_answer_data:Any) -> Any | None:
    if domain in reference_answer_data:
        # Iterate over the answers in the domain
        for answer in reference_answer_data[domain]["answers"]:
            # If the id matches, return the answer
            if answer["id"] == id:
                return answer
    # If the domain does not exist or the id does not match any answer, return None
    return None

# Load webvoyager_data.jsonl
with open('webvoyager_data.jsonl', 'r') as f:
    webvoyager_data = [json.loads(line) for line in f]

# Load reference_answer.json
with open('webvoyager_reference_answer.json', 'r') as f:
    reference_answer_data = json.load(f)


# Combine the data
combined_data = []
index=0
for webvoyager_task in webvoyager_data:
    domain:str=webvoyager_task['web_name']
    id:str=webvoyager_task['id']
    numberical_id:int=int(id.split('--')[1])
    task=webvoyager_task['ques']
    start_url=webvoyager_task['web']
    answer_dict=get_reference_answer(domain, numberical_id, reference_answer_data)
    answer_type:str=answer_dict['type'] # type: ignore
    answer=answer_dict['ans'] # type: ignore

    task_dict= { # type: ignore
        "sites": None,
        "task_id": id,
        "require_login": False,
        "storage_state": None,
        "start_url": start_url,
        "geolocation": None,
        "intent_template": task,
        "instantiation_dict": {},
        "intent": task,
        "require_reset": False,
    }

    if answer_type == "golden":
        task_dict["eval"]= {
            "eval_types": [
                "manual"
            ],
            "reference_answers": {
                 "manual_check": {
                    "answer":answer,
                    "type": answer_type
                }
            },
            "reference_url": None,
            "program_html": None
        }
       # string match eval
    elif answer_type=="possible":
        task_dict["eval"]= {
            "eval_types": [
                "manual"
            ],
            "reference_answers": {
                "manual_check": {
                    "answer":answer,
                    "type": answer_type
                }
            },
            "reference_url": None,
            "program_html": None
        }
    combined_data.append(task_dict) # type: ignore


# Save the combined data to a JSON file
with open('../tasks/webvoyager_test.json', 'w') as f:
    json.dump(combined_data, f, indent=4)
