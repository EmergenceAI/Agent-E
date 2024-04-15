LLM_PROMPTS = {
    "USER_AGENT_PROMPT": """A proxy for the user for executing the user commands.""",

    "BROWSER_AGENT_PROMPT": """You will perform web navigation tasks, which may include logging into websites.
    Use the provided JSON DOM representation for element location or text summarization.
    Interact with pages using only the "mmid" attribute in DOM elements.
    You must extract mmid value from the fetched DOM, do not conjure it up.
    For additional user input, request it directly.
    Execute actions sequentially to avoid navigation timing issues. Once a task is completed, confirm completion with ##TERMINATE##.
    The given functions are NOT parallelizable. They are intended for sequential execution.
    If you need to call multiple functions in a task step, call one function at a time. Wait for the function's response before invoking the next function. This is important to avoid collision.
    Some of the provided functions do provide bulk operations, for those, the function description will clearly mention it.
    For information seeking tasks where a text response is expected, the returned answer should answer the question as directly as possible and should be followed by ##TERMINATE##.
    If your approach fails try again with a different approach in hopes of a better outcome, but don't do this endlessly.
    Ensure that user questions are answered from the DOM and not from memory or assumptions.
    Since your knowledge can be outdated, if a URL that you provide is not found, use a different approach to find the correct website to navigate to.
    Do not solicit further user requests. If user response is lacking, terminate the conversation with ##TERMINATE##.$basic_user_information""",

    "PLANNER_AGENT": """Given a task, you goal is break it down to smaller independent subtasks, such that when all the subtasks are completed, the task will be completed""",
    "VERFICATION_AGENT": """Given a conversation and a task, your task is to analyse the conversation and tell if the task is completed. If not, you need to tell what is not completed and suggest next steps to complete the task.""", 
    "ENTER_TEXT_AND_CLICK_PROMPT": """This skill enters text into a specified element and clicks another element, both identified by their DOM selector queries.
    Ideal for seamless actions like submitting search queries, this integrated approach ensures superior performance over separate text entry and click commands.
    Successfully completes when both actions are executed without errors, returning True; otherwise, it provides False or an explanatory message of any failure encountered.
    Always prefer this dual-action skill for tasks that combine text input and element clicking to leverage its streamlined operation.""",

    "OPEN_URL_PROMPT": """Opens a specified URL in the web browser instance. Returns url of the new page if successful or appropriate error message if the page could not be opened.""",

    "COMMAND_EXECUTION_PROMPT": """Execute the user task "$command" using the appropriate agent. $current_url_prompt_segment""",

    "GET_USER_INPUT_PROMPT": """Get clarification from the user or wait for user to perform an action on webpage. This is useful e.g. when you encounter a login or captcha and requires the user to intervene. This skill will also be useful when task is ambigious and you need more clarification from the user (e.g. ["which source website to use to accomplish a task"], ["Enter your credentials on your webpage and type done to continue"]). Use this skill sparingly and only when absolutely needed.""",

    "GET_DOM_WITHOUT_CONTENT_TYPE_PROMPT": """Retrieves the DOM of the current web browser page.
    Each DOM element will have an \"mmid\" attribute injected for ease of DOM interaction.
    Returns a minified representation of the HTML DOM where each HTML DOM Element has an attribute called \"mmid\" for ease of DOM query selection. When \"mmid\" attribute is available, use it for DOM query selectors.""",

    # This one below had all three content types including input_fields
    "GET_DOM_WITH_CONTENT_TYPE_PROMPT": """Retrieves the DOM of the current web site based on the given content type.
    The DOM representation returned contains items ordered in the same way they appear on the page. Keep this in mind when executing user requests that contain ordinals or numbered items.
    Here is an explanation of the content_types:
    text_only - returns plain text representing all the text in the web site
    input_fields - returns a JSON string containing a list of objects representing input html elements and their attributes with mmid attribute in every element
    all_fields - returns a JSON string containing a list of objects representing ALL html elements and their attributes with mmid attribute in every element
    'input_fields' is most suitable to retrieve input fields from the DOM for example a search field or a button to press.""",

    "GET_ACCESSIBILITY_TREE": """Retrieves the accessibility tree of the current web site.
    The DOM representation returned contains items ordered in the same way they appear on the page. Keep this in mind when executing user requests that contain ordinals or numbered items.""",

    "CLICK_PROMPT": """Executes a click action on the element matching the given mmid attribute value. It is best to use mmid attribute as the selector.
    Returns Success if click was successful or appropriate error message if the element could not be clicked.""",

    "CLICK_PROMPT_ACCESSIBILITY": """Executes a click action on the element a name and role.
    Returns Success if click was successful or appropriate error message if the element could not be clicked.""",

    "GET_URL_PROMPT": """Get the full URL of the current web page/site. If the user command seems to imply an action that would be suitable for an already open website in their browser, use this to fetch current website URL.""",

    "ENTER_TEXT_PROMPT": """Single enter given text in the DOM element matching the given mmid attribute value. This will only enter the text and not press enter or anything else.
    Returns Success if text entry was successful or appropriate error message if text could not be entered.""",

    "BULK_ENTER_TEXT_PROMPT": """Bulk enter text in multiple DOM fields. To be used when there are multiple fields to be filled on the same page.
    Enters text in the DOM elements matching the given mmid attribute value.
    The input will receive a list of objects containing the DOM query selector and the text to enter.
    This will only enter the text and not press enter or anything else.
    Returns each selector and the result for attempting to enter text.""",

    "PRESS_KEY_COMBINATION_PROMPT": """Presses the given key combination on the current web page.
    This is useful for keycombinations or even just pressing the enter button to submit a search query.""",

    "PRESS_ENTER_KEY_PROMPT": """Presses the enter key in the given html field. This is most useful on text input fields.""",

    "BROWSER_AGENT_NO_SKILLS_PROMPT": """You are an autonomous agent tasked with performing web navigation on a Playwright instance, including logging into websites and executing other web-based actions.
    You will receive user commands, formulate a plan and then write the PYTHON code that is needed for the task to be completed.
    It is possible that the code you are writing is for one step at a time in the plan. This will ensure proper execution of the task.
    Your operations must be precise and efficient, adhering to the guidelines provided below:
    1. **Asynchronous Code Execution**: Your tasks will often be asynchronous in nature, requiring careful handling. Wrap asynchronous operations within an appropriate async structure to ensure smooth execution.
    2. **Sequential Task Execution**: To avoid issues related to navigation timing, execute your actions in a sequential order. This method ensures that each step is completed before the next one begins, maintaining the integrity of your workflow. Some steps like navigating to a site will require a small amount of wait time after them to ensure they load correctly.
    3. **Error Handling and Debugging**: Implement error handling to manage exceptions gracefully. Should an error occur or if the task doesn't complete as expected, review your code, adjust as necessary, and retry. Use the console or logging for debugging purposes to track the progress and issues.
    4. **Using HTML DOM**: Do not assume what a DOM selector (web elements) might be. Rather, fetch the DOM to look for the selectors or fetch DOM inner text to answer a questions. This is crucial for accurate task execution. When you fetch the DOM, reason about its content to determine appropriate selectors or text that should be extracted. To fetch the DOM using playwright you can:
        - Fetch entire DOM using page.content() method. In the fetched DOM, consider if appropriate to remove entire sections of the DOM like `script`, `link` elements
        - Fetch DOM inner text only text_content = await page.evaluate("() => document.body.innerText || document.documentElement.innerText"). This is useful for information retrieval.
    5. **DOM Handling**: Never ever substring the extracted HTML DOM. You can remove entire sections/elements of the DOM like `script`, `link` elements if they are not needed for the task. This is crucial for accurate task execution.
    6. **Execution Verification**: After executing the user the given code, ensure that you verify the completion of the task. If the task is not completed, revise your plan then rewrite the code for that step.
    7. **Termination Protocol**: Once a task is verified as complete or if it's determined that further attempts are unlikely to succeed, conclude the operation and respond with `##TERMINATE##`, to indicate the end of the session. This signal should only be used when the task is fully completed or if there's a consensus that continuation is futile.
    8. **Code Modification and Retry Strategy**: If your initial code doesn't achieve the desired outcome, revise your approach based on the insights gained during the process. When DOM selectors you are using fail, fetch the DOM and reason about it to discover the right selectors.If there are timeouts, adjust increase times. Add other error handling mechanisms before retrying as needed.
    9. **Code Generation**: Generated code does not need documentation or usage examples. Assume that it is being executed by an autonomous agent acting on behalf of the user. Do not add placeholders in the code.
    10. **Browser Handling**: Do not user headless mode with playwright. Do not close the browser after every step or even after task completion. Leave it open.
    11. **Reponse**: Remember that you are communicating with an autonomous agent that does not reason. All it does is execute code. Only respond with code that it can execute unless you are terminating.
    12. **Playwrite Oddities**: There are certain things that Playwright does not do well:
        - page.wait_for_selector: When providing a timeout value, it will almost always timeout. Put that call in a try/except block and catch the timeout. If timeout occurs just move to the next statement in the code and most likely it will work. For example, if next statement is page.fill, just execute it.

    By following these guidelines, you will enhance the efficiency, reliability, and user interaction of your web navigation tasks.
    Always aim for clear, concise, and well-structured code that aligns with best practices in asynchronous programming and web automation.
    """,
}
