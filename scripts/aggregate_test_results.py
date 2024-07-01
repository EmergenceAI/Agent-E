import argparse
import json
import os
from collections import Counter
from collections import defaultdict
from typing import Any
from typing import List

import pandas as pd
from pandas.io.formats.style import Styler

URL_ALIAS_MAP = {
    "https://www.allrecipes.com/": "Allrecipes",
    "https://www.amazon.com/": "Amazon",
    "https://www.apple.com/": "Apple",
    "https://arxiv.org/": "Arxiv",
    "https://www.bbc.com/news/": "BBC",
    "https://www.booking.com/": "Booking",
    "https://dictionary.cambridge.org/": "Dictionary",
    "https://www.coursera.org/": "Coursera",
    "https://www.espn.com/": "ESPN",
    "https://github.com/": "GitHub",
    "https://www.google.com/travel/flights/": "Flights",
    "https://www.google.com/maps/": "Maps",
    "https://www.google.com/": "Google",
    "https://huggingface.co/": "Hugging Face",
    "https://www.wolframalpha.com/": "Wolfram"
}

def find_and_read_json_files(test_results_dir: str, target_directory_name: str) -> list[dict[str, Any]]:
    result_data: list[dict[str, Any]] = []

    # Walk through the test results directory
    for root, _dirs, files in os.walk(test_results_dir):
        # Check if the target directory is in the current path
        if target_directory_name in root:
            # If found, iterate through the files in that directory
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    # Read the JSON file and append its contents to the result_data list
                    with open(file_path, 'r') as json_file:
                        print(f"Reading file: {file_path}")
                        try:
                            data = json.load(json_file)
                            result_data.append(data)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from file {file_path}: {e}")

    return result_data

def save_to_json_file(data: Any, output_file: str):
    with open(output_file, 'w') as json_output_file:
        json.dump(data, json_output_file, indent=4)

def extract_alias(url: str) -> str:
    for known_url, alias in URL_ALIAS_MAP.items():
        if url.startswith(known_url):
            return alias
    return "Unknown"

def count_scores_by_alias(data: list[dict[str, Any]]):
    alias_score_counter = defaultdict(Counter)
    overall_score_counter = Counter()
    for entry in data:
        score = entry.get('score')
        start_url = entry.get('start_url')
        if score is not None:
            overall_score_counter[score] += 1
            if start_url:
                alias = extract_alias(start_url)
                alias_score_counter[alias][score] += 1
    return alias_score_counter, overall_score_counter

def calculate_percentages(score_counter: Counter) -> dict[str, float]:
    total_count = sum(score_counter.values())
    score_percentages = {score: (count / total_count) * 100 for score, count in score_counter.items()}
    return score_percentages, total_count

def adjust_scores(data: list[dict[str, Any]], task_ids_to_flip: List[int]):
    for entry in data:
        if entry.get('task_id') in task_ids_to_flip:
            if entry.get('score') == 1.0:
                entry['score'] = 0.0
    return data

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
    parser.add_argument(
        "--adjust_task_ids",
        type=str,
        help="Comma-separated list of task_id values to flip from score 1.0 to 0.0."
    )

    args = parser.parse_args()

    # Derive the full path for the output file
    output_file_path = os.path.join(args.test_results_dir, args.output_file)

    # Find and read the JSON files
    compiled_data = find_and_read_json_files(args.test_results_dir, args.target_directory_name)
    # Sort the compiled data by 'task_index'
    sorted_data: list[dict[str, Any]] = sorted(compiled_data, key=lambda x: x.get('task_index', -1))

    print(f"Number of records found: {len(sorted_data)}")
    # Save the compiled data to a JSON file
    save_to_json_file(sorted_data, output_file_path)

    # Count the scores by alias and overall
    alias_score_counts, overall_score_counts = count_scores_by_alias(sorted_data)

    # Calculate percentages by alias and overall
    alias_score_percentages = {
        alias: calculate_percentages(score_counter)
        for alias, score_counter in alias_score_counts.items()
    }
    overall_score_percentages, overall_total = calculate_percentages(overall_score_counts)

    # Save the alias score percentages to a JSON file
    output_results = {
        "overall": {
            "percentages": overall_score_percentages,
            "counts": dict(overall_score_counts),
            "total": overall_total
        },
        "by_alias": {
            alias: {
                "percentages": percentages,
                "counts": dict(alias_score_counts[alias]),
                "total": total
            }
            for alias, (percentages, total) in alias_score_percentages.items()
        }
    }
    alias_output_file_path = os.path.join(args.test_results_dir, "alias_score_percentages.json")
    save_to_json_file(output_results, alias_output_file_path)

    # Print the overall results to the command line
    print("\nOverall Score Percentages and Counts (Pre-adjustment):")
    print(f"{'Score':<10}{'Percentage':<15}{'Count':<10}")
    for score, percentage in overall_score_percentages.items():
        count = overall_score_counts[score]
        print(f"{score:<10}{percentage:.2f}%{count:<10}")

    # Adjust scores based on provided task IDs
    if args.adjust_task_ids:
        task_ids_to_flip = list(map(int, args.adjust_task_ids.split(',')))
        sorted_data = adjust_scores(sorted_data, task_ids_to_flip)

    # Recount the scores by alias and overall after adjustment
    alias_score_counts_adjusted, overall_score_counts_adjusted = count_scores_by_alias(sorted_data)

    # Recalculate percentages by alias and overall after adjustment
    alias_score_percentages_adjusted = {
        alias: calculate_percentages(score_counter)
        for alias, score_counter in alias_score_counts_adjusted.items()
    }
    overall_score_percentages_adjusted, overall_total_adjusted = calculate_percentages(overall_score_counts_adjusted)

    # Save the adjusted alias score percentages to a JSON file
    adjusted_output_results = {
        "overall": {
            "percentages": overall_score_percentages_adjusted,
            "counts": dict(overall_score_counts_adjusted),
            "total": overall_total_adjusted
        },
        "by_alias": {
            alias: {
                "percentages": percentages,
                "counts": dict(alias_score_counts_adjusted[alias]),
                "total": total
            }
            for alias, (percentages, total) in alias_score_percentages_adjusted.items()
        }
    }
    adjusted_alias_output_file_path = os.path.join(args.test_results_dir, "adjusted_alias_score_percentages.json")
    save_to_json_file(adjusted_output_results, adjusted_alias_output_file_path)

    # Print the overall results to the command line post adjustment
    print("\nOverall Score Percentages and Counts (Post-adjustment):")
    print(f"{'Score':<10}{'Percentage':<15}{'Count':<10}")
    for score, percentage in overall_score_percentages_adjusted.items():
        count = overall_score_counts_adjusted[score]
        print(f"{score:<10}{percentage:.2f}%{count:<10}")

    # Prepare data for DataFrame post adjustment
    data = []
    for score in sorted(set(overall_score_counts_adjusted.keys()).union(*[alias_score_counts_adjusted[alias].keys() for alias in alias_score_counts_adjusted])):
        row = {"Score": score}
        row["Overall"] = f"{overall_score_percentages_adjusted.get(score, 0):.2f}% ({overall_score_counts_adjusted.get(score, 0)})"
        for alias in sorted(URL_ALIAS_MAP.values()):
            percentages, _ = alias_score_percentages_adjusted.get(alias, ({}, 0))
            counts = alias_score_counts_adjusted.get(alias, {})
            row[alias] = f"{percentages.get(score, 0):.2f}% ({counts.get(score, 0)})"
        data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Styling the DataFrame
    styled_df = df.style.set_table_styles(
        [
            {'selector': 'thead th', 'props': 'font-weight: bold; text-align: center;'},
            {'selector': 'th', 'props': 'text-align: center;'},
            {'selector': 'td', 'props': 'text-align: center;'},
            {'selector': 'table', 'props': 'border-collapse: collapse; width: 100%;'},
            {'selector': 'table, th, td', 'props': 'border: 1px solid black;'}
        ]
    ).set_caption("Benchmark Report")

    # Save to HTML with styled format
    html_output_file = os.path.join(args.test_results_dir, "benchmark_report.html")
    styled_df.to_html(html_output_file)

    print(f"\nBenchmark report has been saved to: {html_output_file}")


# Sample how to run:
# python scripts/aggregate_test_results.py /path/to/folder/agent_e_annotators_tests/round2 --adjust_task_ids "14, 26, 51, 63, 93, 141"