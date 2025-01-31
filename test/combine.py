import json
import os

import pandas as pd

# specify the directory containing the JSON files
run_name = "full_text"
base_directory = "/Users/ruhana/Agent-E/new_ruhana_notes/All"  # "/Users/ruhana/Agent-E/ruhana_notes/All/"
expected_task_ids = set(range(0, 642, 1))

results_folder = os.path.join(base_directory, f"results/results_for_test_{run_name}")
log_folder = os.path.join(base_directory, f"logs/test_results_for_{run_name}")

# load the original dataset and annotations
original_annotation_path = "/Users/ruhana/Agent-E/ruhana_notes/baseline_annotated/raw_results.json"  # Replace with your file path
with open(original_annotation_path) as file:
    original_annotation_json = json.load(file)
    original = pd.DataFrame(original_annotation_json)

original = original[["task_id", "score", "tct"]].rename(columns={"score": "original_score", "tct": "original_tct"})

# Load all result (json) files
result_dicts = []
for filename in os.listdir(results_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(results_folder, filename)

        # Load the JSON file
        with open(file_path) as file:
            data = json.load(file)
            result_dicts.append(data)

# Combine all results into one dataframe
df = pd.DataFrame(result_dicts).sort_values(by="task_id")

# Error Checking:
# There are three error cases we would like to check:
# 1) no screenshots taken! (i.e. missing_screenshots)
# 2) validator was not called! (ie. validation_zero)
# 3) workflows where we forcibly ended the task early, (i.e. timeout_runs)
#    **this only exist in one earlier version of the code and was later reverted this! This type of error is not expected to appear!

missing_screenshots = df.loc[df["screenshot_rate"].str.startswith("0/"), "task_id"].tolist()
validation_zero = df.loc[df["validation_count"] == 0, "task_id"].tolist()

# check that timeout was not called
timeout_runs = []
for task_id in df["task_id"]:
    chat_file = f"{log_folder}/logs_for_task_{task_id}/execution_logs_{task_id}.json"
    try:
        with open(chat_file) as file:
            data = json.load(file)
            if "Ending the task early because the task has hit time limit" in str(data):
                timeout_runs.append(task_id)
    except Exception as e:
        print(e)

print("Below are a list of errors. These tasks likely need to be rerun:")
print("\t1) Missing Screenshots:", missing_screenshots)
print("\t2) Validation Zero:", validation_zero)
print("\t3) Timeouts:", timeout_runs)

# Check for missing task_ids
missing_task_ids = sorted(list(expected_task_ids - set(df["task_id"])))
print("Unlabeled task_ids:", missing_task_ids)
print(f"Labled task_ids: {sorted(list(set(df['task_id'])))}")

# All potential reruns
potential_reruns = sorted(list(set(missing_screenshots + validation_zero + timeout_runs + missing_task_ids)))
print(f"\nThere are {len(potential_reruns)} potential reruns: {potential_reruns}")
print(f"\nThere are {len(missing_task_ids)} fully missing: {missing_task_ids}")

# Gather + Summarize Results (make sure to remove all unnecessary tasks first)
summary_json = {}

# # Remove runs with errors!
remove_task_id = validation_zero + timeout_runs + missing_screenshots
df = df[~df["task_id"].isin(remove_task_id)]

# When was validator correct?
df["validator_correct"] = df["score"] == df["validate_score"]


# Merge with original score
df = pd.merge(df, original, on="task_id", how="left")

# Primary Results
print(f"\nFrom {len(df)} samples:")
print(f"Original Agent-E score: {df['original_score'].mean():.4f}")
print(f"Our score: {df['score'].mean():.4f}")
print(f"Our validator score: {df['validator_correct'].mean():.4f}")
print("\n")


print("By Domain:")
start_url_to_task = {
    "https://arxiv.org/": "arxiv",
    "https://dictionary.cambridge.org/": "dictionary",
    "https://github.com/": "github",
    "https://huggingface.co/": "huggingface",
    "https://www.allrecipes.com/": "allrecipes",
    "https://www.amazon.com/": "amazon",
    "https://www.apple.com/": "apple",
    "https://www.bbc.com/news/": "bbc",
    "https://www.booking.com/": "booking",
    "https://www.coursera.org/": "coursera",
    "https://www.espn.com/": "espn",
    "https://www.google.com/": "google",
    "https://www.google.com/maps/": "maps",
    "https://www.google.com/travel/flights/": "flights",
    "https://www.wolframalpha.com/": "wolframalpha",
}
df["start_url"] = df["start_url"].replace(start_url_to_task)

for start_url, group in sorted(df.groupby("start_url")):
    avg_score = group["score"].mean()
    print(f"\t{start_url}: {avg_score:.4f}")


# Secondary Results
# Time per run
df["tct"] = df["tct"]
print()
print(f"Average time: {df['tct'].mean()/60:.4f} +- {df['tct'].std()/60:.4f} minutes")
print()

for start_url, group in sorted(df.groupby("start_url")):
    avg_score = group["tct"].mean()
    print(f"\t{start_url} avg time: {avg_score:.4f}")

# Split the "screenshot_rate" column into two columns
df[["screenshots_taken", "screenshots_attempted"]] = df["screenshot_rate"].str.split("/", expand=True)
df["screenshots_taken"] = df["screenshots_taken"].astype(int)
df["screenshots_attempted"] = df["screenshots_attempted"].astype(int)

# How often were no screenshot taken?
print("Summary of screenshot issue:")
print(f"Missing screenshots occured {len(missing_screenshots)}/{len(df)} times.")
print(f"Total Screenshots Taken: {df['screenshots_taken'].sum()}")
print(f"Total Screenshots Attempted: {df['screenshots_attempted'].sum()}")

print()
# how many times was the validation counted

for val_count, group in sorted(df.groupby("validation_count")):
    avg_score = group["score"].mean()
    original_avg = group["original_score"].mean()
    print(f"Validation called {val_count}: {avg_score*100:.2f}% for {len(group['score'])} tasks,  {original_avg}")


max_validator = max(df["validation_count"])
for count in range(1, max_validator):
    val_column = df[df["validation_count"] <= count]
    val_column = val_column[val_column["validation_count"] > 0]
    accuracy = (val_column["score"].sum()) / len(df)
    print(f"Validator called {count} accuracy: {accuracy}")

print(list(df[(df["validation_count"] > 1) & (df["score"] == 1.0)]["task_id"]))

exit()
