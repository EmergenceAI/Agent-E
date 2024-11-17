import json
import random
from collections import defaultdict

# Load the JSON data
with open('webvoyager_test.json', 'r') as file:
    data = json.load(file)

# Group items by start_url
grouped_data = defaultdict(list)
for item in data:
    grouped_data[item['start_url']].append(item)

# Sample 4 unique items for each unique start_url
sampled_data = []
sampled_set = set()
for start_url, items in grouped_data.items():
    unique_items = [item for item in items if item['task_id'] not in sampled_set]
    sampled_items = random.sample(unique_items, min(5, len(unique_items)))
    sampled_data.extend(sampled_items)
    sampled_set.update(item['task_id'] for item in sampled_items)

    # Print analytics for each category
    print(f"Category: {start_url}")
    print("Task IDs:", [item['task_id'] for item in sampled_items])
    print(f"Total number of tasks: {len(sampled_items)}\n")

# Sort the sampled data by task_id
sampled_data.sort(key=lambda x: x['task_id'])

# Write the sampled data to a new file
with open('sampled_webvoyager_test.json', 'w') as file:
    json.dump(sampled_data, file, indent=2)

print("Sampled data has been written to 'sampled_webvoyager_test.json'")