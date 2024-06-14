import argparse
import json
import os
from collections import Counter
from typing import Any


def find_and_read_json_files(test_results_dir: str, target_directory_name: str):
    result_data: list[dict[str, Any]] = []

    # Walk through the test results directory
    for root, _dirs, files in os.walk(test_results_dir):
        # Check if the target directory is in the current path
        if target_directory_name in root:
            # If found, iterate through the files in that directory
            for file in files:
                print("Just saw file: ", file)
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    print("Reading contents of file: ", file_path)
                    # Read the JSON file and append its contents to the result_data list
                    with open(file_path, 'r') as json_file:
                        try:
                            data = json.load(json_file)
                            result_data.append(data)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from file {file_path}: {e}")

    return result_data

def save_to_json_file(data: list[dict[str, Any]], output_file: str):
    with open(output_file, 'w') as json_output_file:
        json.dump(data, json_output_file, indent=4)

def count_scores(data):
    score_counter = Counter()
    for entry in data:
        score = entry.get('score')
        if score is not None:
            score_counter[score] += 1
    return score_counter

def calculate_percentages(score_counter, total_count):
    score_percentages = {}
    for score, count in score_counter.items():
        percentage = (count / total_count) * 100
        score_percentages[score] = (percentage, count)
    return score_percentages

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some JSON files.")
    parser.add_argument(
        "test_results_dir",
        type=str,
        help="The base directory containing the test results."
    )
    parser.add_argument(
        "--target_directory_name",
        type=str,
        default="results_for_test_results_for_webvoyager_test",
        help="The name of the target directory to search within the base directory."
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="compiled_test_results.json",
        help="The name of the output file."
    )

    args = parser.parse_args()

    # Derive the full path for the output file
    output_file_path = os.path.join(args.test_results_dir, args.output_file)

    # Find and read the JSON files
    compiled_data = find_and_read_json_files(args.test_results_dir, args.target_directory_name)
    # Sort the compiled data by 'task_index'
    sorted_data: list[dict[str, Any]] = sorted(compiled_data, key=lambda x: x.get('task_index', -1))

    print("Number of records found: ", len(sorted_data))
    # Save the compiled data to a JSON file
    save_to_json_file(sorted_data, output_file_path)

    # Count the scores
    score_counts = count_scores(sorted_data)

    # Calculate percentages
    total_scores = sum(score_counts.values())
    score_percentages = calculate_percentages(score_counts, total_scores)

    # Print the results
    print(f"Compiled and sorted data has been saved to: {output_file_path}")
    print("Score counts and percentages:")
    for score, (percentage, count) in score_percentages.items():
        print(f"{score}: {percentage:.2f}% ({count})")

