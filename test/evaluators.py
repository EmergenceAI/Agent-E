"""base class for evaluation"""
import collections
import html
import time
import urllib
import urllib.parse
from test.test_utils import clean_answer
from test.test_utils import evaluate_exact_match
from test.test_utils import evaluate_fuzzy_match
from test.test_utils import evaluate_must_include
from test.test_utils import evaluate_ua_match
from typing import Any

from ae.utils.logger import logger
from playwright.sync_api import CDPSession
from playwright.sync_api import Page
from termcolor import colored


class Evaluator:
    """Base class for evaluation strategies.

    Attributes:
        eval_tag (str): A tag to identify or categorize the evaluator.
    """

    def __init__(self, eval_tag: str = "") -> None:
        """Initialize the evaluator with an optional evaluation tag."""
        self.eval_tag = eval_tag

    async def __call__(self, task_config: dict[str, Any], page: Page, client: CDPSession, answer: str) -> dict[str, float|str]:
        """Abstract method to be implemented by subclasses for evaluation.

        Raises:
            NotImplementedError: This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")


class StringEvaluator(Evaluator):
    """Evaluates string-based answers using various matching criteria.

    Supports exact matches, some matches, fuzzy matching using LLM, and unachievable task matching.
    """

    async def __call__(
        self,
        task_config: dict[str, Any],
        page: Page | None = None,
        client: CDPSession | None = None,
        answer: str | None = None,

    ) -> dict[str, float|str]:
        last_action = answer or ""
        pred = clean_answer(last_action)

        score = 1.0
        for approach, value in task_config["eval"]["reference_answers"].items():

            match approach:
                case "exact_match":
                    logger.info(f"Evaluating exact_match for answer: Predicted: {pred} , Reference: {value}")
                    score *= evaluate_exact_match(ref=value, pred=pred)

                case "must_include":
                    logger.info(f"Evaluating must_include for answer: \"{answer}\" to see if it includes the expeced values: \"{value}\"\n")
                    assert isinstance(value, list)
                    for must_value in value: # type: ignore
                        score *= evaluate_must_include(
                            ref=must_value, # type: ignore
                            pred=pred,
                            tokenize=(len(value) == 1), # type: ignore
                        )
                case "some_matches":
                    min_required_matches = value.get("min_required", 1)
                    matches = sum(evaluate_must_include(ref=phrase, pred=pred, tokenize=False) for phrase in value["phrases"])
                    score *= float(matches >= min_required_matches)
                case "fuzzy_match":
                    logger.info(f"Evaluating fuzzy_match for answer: {answer}")
                    intent = task_config["intent"]
                    if value == "N/A":
                        # if the instruction only asks the model to generate N/A when encountering an unachievable task
                        # without more concrete reasons
                        score *= evaluate_exact_match(ref=value, pred=pred)
                        # if the instruction also asks the model to generate the reason why the task is unachievable
                        # this should be the default as it will prevent false positive N/A`
                        if score != 1:
                            score = 1.0 * evaluate_ua_match(
                                intent=task_config["intent"],
                                ref=task_config["eval"]["string_note"],
                                pred=pred,
                            )
                    else:
                        logger.info(f"Evaluating generic for answer: {answer}")
                        assert isinstance(value, list)
                        for reference in value: # type: ignore
                            score *= evaluate_fuzzy_match(
                                ref=reference, pred=pred, intent=intent # type: ignore
                            )
                case _:
                    logger.info(f"Unknown approach value received: {approach}")
        return {"score": score}


class URLEvaluator(Evaluator):
    """Evaluates if the given URL matches the expected URL criteria defined in the configuration.

    This includes checking if the base path of the URL and its query parameters match those specified in the reference URLs.
    """

    async def __call__(
        self,
        task_config: dict[str, Any],
        page: Page,
        client: CDPSession | None = None,
        answer: str | None = None
    ) -> dict[str, float|str]:
        """Evaluates the current page URL against reference URLs specified in the config file.

        Parameters:
            task_config (dict[str, Any]): The task configuration containing evaluation criteria.
            page (Page): The Playwright page object for the current webpage.
            client (CDPSession | None, optional): The Chrome DevTools Protocol session object. Not used in this evaluator.
            answer (str | None, optional): Not used in this evaluator.

        Returns:
            dict[str, float|str]: "score" 1.0 if the page URL matches any of the reference URLs, considering the matching rule; otherwise 0.0.

        Raises:
            ValueError: If an unknown matching rule is specified in the config file.
        """

        def clean_url(url: str) -> str:
            url = str(url)
            url = url.rstrip("/")
            url = url.lower()
            return url

        def parse_url(url: str) -> tuple[str, dict[str, list[str]]]:
            """Parse a URL into its base, path, and query components."""
            parsed_url = urllib.parse.urlparse(url)
            base_path = parsed_url.netloc + parsed_url.path
            query = urllib.parse.parse_qs(parsed_url.query)
            return base_path, query

        def parse_urls(
            urls: list[str],
        ) -> tuple[list[str], dict[str, set[str]]]:
            """Parse a list of URLs."""
            base_paths: list[str] = []
            queries: dict[str, set[str]] = collections.defaultdict(set)
            for url in urls:
                base_path, query = parse_url(url)
                base_paths.append(base_path)
                for k, v in query.items():
                    queries[k].update(v)
            return base_paths, queries

        pred = clean_url(page.url)
        ref_urls = task_config["eval"]["reference_url"].split(" |OR| ")
        ref_urls = [clean_url(url) for url in ref_urls]
        matching_rule = task_config["eval"].get("url_note", "GOLD in PRED")
        if matching_rule == "GOLD in PRED":
            ref_base_paths, ref_queries = parse_urls(ref_urls)
            pred_base_paths, pred_query = parse_url(pred)

            base_score = float(
                any(
                    [
                        ref_base_path in pred_base_paths
                        for ref_base_path in ref_base_paths
                    ]
                )
            )
            query_score = 1.0
            for k, possible_values in ref_queries.items():
                query_score *= float(
                    any(
                        possible_ref_value in pred_query.get(k, [])
                        for possible_ref_value in possible_values
                    )
                )
            score = base_score * query_score

        else:
            raise ValueError(f"Unknown matching rule: {matching_rule}")

        return {"score": score}


class HTMLContentEvaluator(Evaluator):
    """Evaluates if specified HTML content or elements appear on the webpage.

    This involves navigating to URLs specified in the configuration and checking for the presence of HTML elements or content using various strategies.
    """

    async def __call__(
        self,
        task_config: dict[str, Any],
        page: Page,
        client: CDPSession | None = None,
        answer: str | None = None
    ) -> dict[str, float|str]:
        """Evaluates the presence of specified HTML content on the webpage.

        Parameters:
            task_config (dict[str, Any]): The task configuration containing evaluation criteria.
            page (Page): The Playwright page object for the current webpage.
            client (CDPSession | None, optional): The Chrome DevTools Protocol session object. Not used in this evaluator.
            answer (str | None, optional): Not used in this evaluator.

        Returns:
            dict[str, float|str]: "score" A score between 0.0 and 1.0 representing the presence of required HTML content on the webpage.

        Raises:
            ValueError: If an unknown locator strategy is specified in the config file.
        """
        targets = task_config["eval"]["program_html"]

        score = 1.0
        for target in targets:
            target_url: str = target["url"]  # which url to check
            if target_url.startswith("func"):
                func = target_url.split("func:")[1]
                func = func.replace("__last_url__", page.url)
                target_url = eval(func)

            locator: str = target["locator"]  # js element locator

            # navigate to that url
            if target_url != "last":
                page.goto(target_url)
                time.sleep(3)

            # empty, use the full page
            if not locator.strip():
                selected_element = page.content()
            # use JS to select the element
            elif locator.startswith("document.") or locator.startswith("[...document.") or locator.startswith("jsblock:"):
                if "prep_actions" in target:
                    try:
                        for prep_action in target["prep_actions"]:
                            page.evaluate(f"() => {prep_action}")
                    except Exception:
                        pass
                try:
                    if locator.startswith("jsblock:"):
                        locator = locator.split("jsblock:")[1]

                    selected_element = str(await page.evaluate(f"() => {locator}"))
                    if not selected_element:
                        selected_element = ""
                except Exception:
                    # the page is wrong, return empty
                    selected_element = ""
            # run program to call API
            elif locator.startswith("func:"):  # a helper function
                func = locator.split("func:")[1]
                func = func.replace("__page__", "page")
                selected_element = eval(func)
            else:
                raise ValueError(f"Unknown locator: {locator}")

            selected_element = html.unescape(selected_element)

            if "exact_match" in target["required_contents"]:
                required_contents = target["required_contents"]["exact_match"]
                cur_score = evaluate_exact_match(
                    ref=required_contents, pred=selected_element
                )
                score *= float(cur_score)
                # logger.info(f"[exact match] {cur_score}, selected element: {selected_element}, required contents: {required_contents}")
            elif "must_include" in target["required_contents"]:
                required_contents = target["required_contents"]["must_include"]
                assert isinstance(required_contents, list)
                for content in required_contents: # type: ignore
                    content_or = content.split(" |OR| ") # type: ignore
                    cur_score = any(
                        [
                            evaluate_must_include(
                                ref=content, # type: ignore
                                pred=selected_element,
                                tokenize=False,
                            )
                            for content in content_or # type: ignore
                        ]
                    )
                    score *= float(cur_score)
                    # logger.info(f"[must include] {cur_score}, selected element: {selected_element}, required contents: {content_or}")
            else:
                raise ValueError(
                    f"Unknown required_contents: {target['required_contents'].keys()}"
                )
        return {"score": score}

class ManualContentEvaluator(Evaluator):
    """Evaluation Route for Manual Evaluation."""
    async def __call__(
        self,
        task_config: dict[str, Any],
        page: Page,
        client: CDPSession | None = None,
        answer: str | None = None
    ) -> dict[str, float|str]:
        """Pauses Execution to get manual evaluation score from user.

        Parameters:
            task_config (dict[str, Any]): The task configuration containing evaluation criteria.
            page (Page): The Playwright page object for the current webpage.
            client (CDPSession | None, optional): The Chrome DevTools Protocol session object. Not used in this evaluator.
            answer (str | None, optional): Not used in this evaluator.

        Returns:
            dict[str, float|str]: A score representig the status 1 = pass, 0 = fail and -0.1 is a skip. Additionaly, a reason can be provided for the score (mainly for fail/skip).
        """
        task = task_config["intent"]
        reference_answer = task_config["eval"]["reference_answers"]["manual_check"]["answer"]
        answer_type = task_config["eval"]["reference_answers"]["manual_check"]["type"]
        id = str(task_config["task_id"])
        index = str(task_config["task_index"])

        print(colored("\n\n***************************\n", "green", attrs=["bold"]))
        print(colored("Task ID: ", "blue", attrs=["bold"]) + id + "\n")
        print(colored("Task Index: ", "blue", attrs=["bold"]) + index + "\n")
        print(colored("Task: ", "blue", attrs=["bold"]) + task + "\n")
        print(colored("Agent answer: ", "blue", attrs=["bold"]) + str(answer or "") + "\n")

        if answer_type.strip().lower() == "possible":
            print(colored("Possible answer (reference): ", "yellow") + f"~~~{reference_answer}~~~")
        elif answer_type.strip().lower() == "golden":
            print(colored("Golden answer (reference): ", "yellow") + reference_answer)

        user_response = input(colored("Annotate the task as Pass, Fail or Skip (please use Skip sparingly)? ", "magenta", attrs=["bold"]))
        eval_response: dict[str, float|str] = {}
        if(user_response.lower()=="pass"):
            eval_response["score"] = 1.0
        elif user_response.lower()=="fail":
            eval_response["score"] = 0.0
        elif user_response.lower()=="skip":
            eval_response["score"] = -0.1
        else:
            print(colored(f"Received response: {user_response}", "red"))
            raise ValueError("Invalid user response. Please enter 'Pass', 'Fail' or 'Skip'.")
        reason: str|None = None

        if eval_response["score"] <= 0:
            reason = input("Reason for rating: ")
            eval_response["reason"] = reason

        return eval_response

class EvaluatorComb(Evaluator):
    """Combines multiple evaluators to perform a comprehensive evaluation based on different criteria.

    Attributes:
        evaluators (list[Evaluator]): A list of evaluator instances to be used for evaluation.
    """

    def __init__(self, evaluators: list[Evaluator]) -> None:
        """Initializes the composite evaluator with a list of individual evaluators.

        Parameters:
            evaluators (list[Evaluator]): The list of evaluators to include in the composite evaluation.
        """
        self.evaluators = evaluators


    async def __call__(
        self,
        task_config: dict[str, Any],
        page: Page,
        client: CDPSession,
        answer: str,
    ) -> dict[str, float|str]:
        """Performs the evaluation using all included evaluators and aggregates their scores.

        Parameters:
            task_config (dict[str, Any]): The task configuration containing evaluation criteria.
            page (Page): The Playwright page object for the current webpage.
            client (CDPSession): The Chrome DevTools Protocol session object.
            answer (str): The answer or content to be evaluated.

        Returns:
            dict[str, float|str]: "score" - The aggregated score from all evaluators, representing the overall evaluation result. "reason" - The reason for the evaluation score, if applicable.
        """
        score: float = 1.0
        reason: str | None = None
        for evaluator in self.evaluators:
            eval_result = await evaluator(task_config, page, client, answer)
            score: float = score * eval_result["score"] # type: ignore
            if "reason" in eval_result:
                if reason is None:
                    reason = eval_result["reason"] # type: ignore
                else:
                    reason += f"\n{eval_result['reason']}"
        return {"score": score, "reason": reason} # type: ignore


def evaluator_router(task_config: dict[str, Any]) -> EvaluatorComb:
    """Creates and configures a composite evaluator based on the evaluation types specified in the configuration file.

    Parameters:
        task_config dict[str, Any]: configuration specifying the evaluation types to use.

    Returns:
        EvaluatorComb: A composite evaluator configured with the specified types of individual evaluators.

    Raises:
        ValueError: If an unsupported evaluation type is specified in the configuration file.
    """

    eval_types = task_config["eval"]["eval_types"]
    evaluators: list[Evaluator] = []
    for eval_type in eval_types:
        match eval_type:
            case "string_match":
                logger.info("Adding string evaluator")
                evaluators.append(StringEvaluator())
            case "url_match":
                logger.info("Adding URL evaluator")
                evaluators.append(URLEvaluator())
            case "program_html":
                logger.info("Adding HTML evaluator")
                evaluators.append(HTMLContentEvaluator())
            case "manual":
                logger.info("Adding manual evaluator")
                evaluators.append(ManualContentEvaluator())
            case _:
                raise ValueError(f"eval_type {eval_type} is not supported")

    return EvaluatorComb(evaluators)
