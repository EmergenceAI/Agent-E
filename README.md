# Agent-E
**[Try our cloud version](https://www.emergence.ai/web-automation-api)**

<img src="./docs/images/QR.png" alt="QR code." width="200">


[Discord](https://discord.gg/wgNfmFuqJF) &nbsp;&nbsp; [Cite paper](https://arxiv.org/abs/2407.13032) _Note: The WebVoyager validation used [nested_chat_for_hierarchial_planning branch](https://github.com/EmergenceAI/Agent-E/tree/nested_chat_for_hierarchial_planning) and GPT4-Turbo_


Agent-E is an agent based system that aims to automate actions on the user's computer. At the moment it focuses on automation within the browser. The system is based on on [AutoGen agent framework](https://github.com/microsoft/autogen).

This provides a natural language way to interacting with a web browser:
- Fill out forms (web forms not PDF yet) using information about you or from another site
- Search and sort products on e-commerce sites like Amazon based on various criteria, such as bestsellers or price.
- Locate specific content and details on websites, from sports scores on ESPN to contact information on university pages.
- Navigate to and interact with web-based media, including playing YouTube videos and managing playback settings like full-screen and mute.
- Perform comprehensive web searches to gather information on a wide array of topics, from historical sites to top local restaurants.
- Manage and automate tasks on project management platforms (like JIRA) by filtering issues, easing the workflow for users.
- Provide personal shopping assistance, suggesting products based on the user's needs, such as storage options for game cards.

While Agent-E is growing, it is already equipped to handle a versatile range of tasks, but the best task is the one that you come up with. So, take it for a spin and tell us what you were able to do with it. For more information see our [blog article](https://www.emergence.ai/blog/distilling-the-web-for-multi-agent-automation).


## Quick Start Using Scripts
To get started with Agent-E, follow the steps below to install dependencies and configure your environment.
#### 1. Run the Installation Script

- **macOS/Linux**:
  - From the project root, run the following command to set up the environment and install all dependencies:
    ```bash
    ./install.sh
    ```
    - For **Playwright support**, you can pass the `-p` flag to install Playwright without further prompting:
      ```bash
      ./install.sh -p
      ```

- **Windows**:
  - From the project root, execute the following command in PowerShell:
    ```powershell
    .\win_install.ps1
    ```
    - To install Playwright without further prompting, add the `-p` flag:
      ```powershell
      .\win_install.ps1 -p
      ```
#### 2. Configure Environment Variables
- Go to the newly created `.env` and `agents_llm_config.json` and follow the instructions to set the fields

#### 3. Run Agent-E
Once you have set up the environment and installed all the dependencies, you can run Agent-E using the following command:
```bash
python -m ae.main
```

**For macOS Users**
```bash
python -u -m ae.main
```


## Manual Setup

### 1. Install `uv`
Agent-E uses `uv` to manage the Python virtual environment and package dependencies.

- **macOS/Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh

- **Windows**:
  ```bash
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

- Alternatively, you can install `uv` using `pip`: `pip install uv`

### 2. Set up the virtual environment
Use `uv` to create and activate a virtual environment for the project.
```bash
uv venv --python 3.11  # 3.10+ should also work
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
Generate the `requirements.txt` file from the `pyproject.toml` and install dependencies.
```bash
uv pip compile pyproject.toml -o requirements.txt
uv pip install -r requirements.txt
```

To install extras for development, run:
```bash
uv pip install -r pyproject.toml --extra dev
```

### 4.(Optional) Install Playwright Drivers
If you do not have Google Chrome installed locally and don’t want to install it, you can use Playwright for browser automation.
```bash
playwright install
```

### 5. Configure the environment
Create a `.env` file by copying the provided example file.
```bash
cp .env-example .env
```
- Edit the `.env` file and set the following variables:
    - `AUTOGEN_MODEL_NAME` (e.g., `gpt-4-turbo` for optimal performance).
    - `AUTOGEN_MODEL_API_KEY` LLM API key.
    - If using a model other than OpenAI, configure `AUTOGEN_MODEL_BASE_URL` (url where the completion endpoint is hosted, but don't put `/completion` in it), `AUTOGEN_MODEL_API_TYPE`, and `AUTOGEN_MODEL_API_VERSION`.
- Optionally configure `AUTOGEN_LLM_TEMPERATURE` and `AUTOGEN_LLM_TOP_P`.
- If you want to use local chrome browser over playwright browser, go to chrome://version/ in chrome, find the path to your profile and set `BROWSER_STORAGE_DIR` to the path value

## Environment Variables

Agent-E relies on several environment variables for its configuration. You need to define these in a `.env` file in the project root. A sample `.env-example` file is provided for convenience.

### Key Variables:

- **`AUTOGEN_MODEL_NAME`**  
  Name of the LLM model you want to use (e.g., `gpt-4-turbo`). This is required for most setups.
  
- **`AUTOGEN_MODEL_API_KEY`**  
  Your API key for accessing the LLM model (e.g., OpenAI API key).
  
- **`AUTOGEN_MODEL_BASE_URL`** *(optional)*  
  Base URL for the model if it's hosted on a service other than OpenAI (e.g., Azure OpenAI services). Example:  
  `https://api.groq.com/openai/v1`  
  or  
  `https://<YOUR_AZURE_ENDPOINT>.openai.azure.com`

- **`AUTOGEN_MODEL_API_TYPE`** *(optional)*  
  Type of model API (e.g., `azure` for Azure-hosted models).

- **`AUTOGEN_MODEL_API_VERSION`** *(optional)*  
  Version of the model API to use, typically needed for Azure models (e.g., `2023-03-15-preview`).

- **`AUTOGEN_LLM_TEMPERATURE`** *(optional)*  
  Sets the temperature for the LLM. Controls randomness in output. Defaults to `0.0` for `gpt-*` models.

- **`AUTOGEN_LLM_TOP_P`** *(optional)*  
  Sets the top-p value, which controls the diversity of token sampling. Defaults to `0.001` for `gpt-*` models.

- **`BROWSER_STORAGE_DIR`** *(optional)*  
  Path to your local Chrome browser profile, required if using a local Chrome instance instead of Playwright.

- **`SAVE_CHAT_LOGS_TO_FILE`**  
  Set to `true` or `false` (Default: `true`). Indicates whether to save chat logs to a file or print them to stdout.

- **`LOG_MESSAGES_FORMAT`**  
  Set to `json` or `text` (Default: `text`). Specifies the format for logging messages.

- **`ADDITIONAL_SKILL_DIRS`** *(optional)*
  A comma-separated list of directories or `.py` files where additional skills can be loaded from. This is used to dynamically load skills from specified directories or files.
  Example: `ADDITIONAL_SKILL_DIRS="./private_skills,./extra_skills/my_custom_skill.py"` would be added to the `.env` file (or equivalent)

- **`PLANNER_USER_INPUT_SKILL_ENABLED`** *(optional)*
  Set to `true` or `false` (Default: `false`). Specifies whether to allow the planner agent to get user input or not.
  
## Running the Code

Once you have set up the environment and installed all the dependencies, you can run Agent-E using `./run.sh` script or using the following command:
```bash
python -m ae.main
```

### For macOS Users
If you encounter `BlockingIOError` (Errno 35) when running the program on macOS, execute the following command to avoid the issue:
```bash
python -u -m ae.main
```

### Expected Behavior
Once Agent-E is running, you should see an icon in the browser interface. Clicking on this icon will open a chat-like interface where you can input natural language commands. Example commands you can try:
- `open youtube and search for funny cat videos`
- `find iPhone 14 on Amazon and sort by best seller`

## Advanced Usage

### Launch via Web Endpoint

Agent-E provides a FastAPI wrapper, allowing you to send commands via HTTP and receive streaming results. This feature is useful for programmatic task automation or integrating Agent-E into larger systems.

#### To launch the FastAPI server:

1. On Linux/macOS, run the following command:
   ```bash
   uvicorn ae.server.api_routes:app --reload --loop asyncio
   ```
2. On Windows, run the same command but without ```--reload``` (Python still has different async implementations across OSes, removing --reload helping finding a workaround, see this [answer on  StackOverflow](https://stackoverflow.com/a/78795990)):
   ```cmd
   uvicorn ae.server.api_routes:app --loop asyncio
   ```

2. Send POST requests to execute tasks. For example, to execute a task using cURL:
```bash
curl --location 'http://127.0.0.1:8000/execute_task' \
--header 'Content-Type: application/json' \
--data '{
    "command": "go to espn, look for soccer news, report the names of the most recent soccer champs"
}'
```
Optionally, the API request can include an llm_config object if you want to apply a different configuration during API request execution. The llm_config object should have configuration seperately for planner_agent and browser_nav_agent. See  `agents_llm_config-example.json` for an exmaple.

```bash
curl --location 'http://127.0.0.1:8000/execute_task' \
--header 'Content-Type: application/json' \
--data '{
    "command": "go to espn, look for soccer news, report the names of the most recent soccer champs",
    "llm_config":{"planner_agent":{...}, "browser_nav_agent":{...}}
}'
```
### Customizing LLM Parameters
Agent-E supports advanced LLM configurations using environment variables or JSON-based configuration files. This allows users to customize how the underlying model behaves, such as setting temperature, top-p, and model API base URLs.

To configure Agent-E using a JSON file, add the following to your `.env` file:
```makefile
AGENTS_LLM_CONFIG_FILE=agents_llm_config.json
AGENTS_LLM_CONFIG_FILE_REF_KEY=openai_gpt
```
A sample JSON config file is provided in the project root: `agents_llm_config-example.json`.


#### Default Values for LLM Parameters
If you do not set `temperature`, `top_p`, or `seed` in your `.env` file or JSON configuration, Agent-E will use the following default values:
- For `gpt-*` models:
    - `"temperature": 0.0`
    - `"top_p": 0.001`
    - `"seed": 12345`
- For other models:
    -  `"temperature": 0.1`
    - `"top_p": 0.1`

## Open-source Models

Agent-E supports the use of open-source models through LiteLLM and Ollama. This allows users to run language models locally on their machines, with LiteLLM translating OpenAI-format inputs to local models' endpoints.

### Steps to Use Open-source Models:

1. **Install LiteLLM**:
    ```bash
    pip install 'litellm[proxy]'
    ```

2. **Install Ollama**:
    - For Mac and Windows, download [Ollama](https://ollama.com/download).
    - For Linux:
        ```bash
        curl -fsSL https://ollama.com/install.sh | sh
        ```

3. **Pull Ollama Models**:
    Before using a model, download it from the library. The list of available models is [here](https://ollama.com/library). For example, to pull the Mistral v0.3 model:
    ```bash
    ollama pull mistral:v0.3
    ```

4. **Run LiteLLM**:
    Start the LiteLLM proxy using the downloaded model:
    ```bash
    litellm --model ollama_chat/mistral:v0.3
    ```

5. **Configure Model in AutoGen**:
    Modify your `.env` file as follows. No model name or API keys are required since the model is running locally.
    ```bash
    AUTOGEN_MODEL_NAME=NotRequired
    AUTOGEN_MODEL_API_KEY=NotRequired
    AUTOGEN_MODEL_BASE_URL=http://0.0.0.0:400
    ```

### Notes:
- Running local Large Language Models (LLMs) with Agent-E is possible, but has not been thoroughly tested. Use this feature with caution.


## Troubleshooting

Below are some common issues you may encounter when setting up or running Agent-E, along with steps to resolve them.

### 1. pip not installed in the virtual environment

If you encounter an issue where `pip` is not installed in the virtual environment after setup, follow these steps:

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

2. Install `pip`:
```bash
python -m ensurepip --upgrade
```

3. Deactivate the virtual environment:
```bash
deactivate
```

4. Reactivate the virtual environment:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

5. Check for `pip` in the `.venv/bin` directory. You should now have `pip` installed.

### 2. BlockingIOError on macOS
If you are on `macOS` and encounter the following error:
```
BlockingIOError: [Errno 35] write could not complete without blocking
```
This happens when AutoGen tries to print large amounts of text to the terminal. To fix this, run the following command with the `-u` flag to make output unbuffered:
```bash
python -u -m ae.main
```
Note: Using unbuffered output may result in some output not appearing in the terminal.

### 3. Playwright driver issues
If you do not have Google Chrome installed locally and run into issues with browser automation, install the Playwright drivers:
```bash
playwright install
```
Playwright will install the necessary browser binaries to run the automation tasks without needing Chrome locally installed.

### 4. Chrome profile not found
If you want to use your local Chrome browser instead of Playwright and encounter issues finding the browser profile path, follow these steps:

1. Open Chrome and go to `chrome://version/`.
2. Locate the `Profile Path`.
3. Set the `BROWSER_STORAGE_DIR` environment variable in the `.env` file to this path:
```
BROWSER_STORAGE_DIR=/path/to/your/chrome/profile
```

If you encounter other issues, please refer to the project’s [GitHub issues](https://github.com/EmergenceAI/Agent-E/issues) or reach out on [Discord](https://discord.gg/wgNfmFuqJF) for assistance.


## Demos

| Video | Command | Description |
|-----------|-------------|-------------|
| [![Oppenheimer Video](docs/images/play-video-on-youtube-thumbnail.png)](https://www.youtube.com/embed/v4BgYiDHNZs) | There is an Oppenheimer video on youtube by Veritasium, can you find it and play it? | <ul> <li>Navigates to www.youtube.com </li> <li>Searches for Oppenheimer Veritasium using the searchbar </li> <li> Plays the correct video </li></ul>|
| [![Example 2: Use information to fill forms](docs/images/form-filling-thumbnail.png)](https://www.youtube.com/embed/uyE7tfKkB0E) | Can you do this task? Wait for me to review before submitting. | Takes the highlighted text from the email as part of the instruction. <ul> <li>Navigates to the form URL </li> <li>Identifies elements in the form to fill </li> <li> Fills the form using information from memory defined in user preferences.txt </li> <li>Waits for user to review before submitting the form </li> |
| [![Example 3: Find and add specific product to amazon cart](docs/images/amazon-add-to-cart-thumbnail.png)](https://www.youtube.com/embed/CiKZwU_F6TQ) | Find Finish dishwasher detergent tablets on amazon, sort by best seller and add the first one to my cart | <ul> <li> Navigates to www.amazon.com </li> <li>Searches for Finish dishwasher detergent tablets using amazon search feature </li> <li> Sorts the search results by best seller </li> <li>Selects the first product to navigate to the the product page of the first product. </li> <li> Adds the product to cart </li></ul> |
| [![Example 4: Compare flight prices on Google Flights](docs/images/compare-flights-thumbnail.png)](https://www.youtube.com/embed/JDtnMx0pTmQ) | Compare business class flight options from Lisbon to Singapore for a one-way trip on September 15, 2024 on Google Flights? | <ul><li>  </li> <li> Sets Journey type to one-way. </li> <li> Sets number of passengers to one. </li> <li> Sets departure date to 15 September </li> <li> Sets date to September 15 2024 </li> <li> Sets ticket type to business class </li> <li> Executes search </li> <li> Sets departure date to 15 September </li> Extracts flight information</ul>|



## Architecture

![Agent-E system view](docs/images/agent-e-system-architecture.png?raw=true "Agent-E system view")

Building on the foundation provided by the [AutoGen agent framework](https://github.com/microsoft/autogen), Agent-E's architecture leverages the interplay between skills and agents. Each skill embodies an atomic action, a fundamental building block that, when executed, returns a natural language description of its outcome. This granularity allows Agent-E to flexibly assemble these skills to tackle complex web automation workflows.

![Agent-E AutoGen setup](docs/images/agent-e-autogen-setup.png?raw=true "Agent-E AutoGen setup")

The diagram above shows the configuration chosen on top of AutoGen. The skills can be partitioned differently, but this is the one that we chose for the time being. We chose to use skills that map to what humans learn about the web browser rather than allow the LLM to write code as it pleases. We see the use of configured skills to be safer and more predictable in its outcomes. Certainly it can click on the wrong things, but at least it is not going to execute malicious unknown code.

### Agents
At the moment there are two agents, the User proxy (executes the skills), and Browser navigation. Browser navigation agent embodies all the skills for interacting with the web browser.

### Skills Library
At the core of Agent-E's capabilities is the Skills Library, a repository of well-defined actions that the agent can perform; for now web actions. These skills are grouped into two main categories:

- **Sensing Skills**: Skills like `get_dom_with_content_type` and `geturl` that help the agent understand the current state of the webpage or the browser.
- **Action Skills**: Skills that allow the agent to interact with and manipulate the web environment, such as `click`, `enter text`, and `open url`.

Each skill is created with the intention to be as conversational as possible, making the interactions with LLMs more intuitive and error-tolerant. For instance, rather than simply returning a boolean value, a skill might explain in natural language what happened during its execution, enabling the LLM to better understand the context and correct course if necessary.

Below are the skills we have implemented:

| Sensing Skills | Action Skills |
|----------------|---------------|
| `geturl` - Fetches and returns the current url. | `click` - given a DOM query selector, this will click on it. |
| `get_dom_with_content_type` - Retrieves the HTML DOM of the active page based on the specified content type. Content type can be:<br> - `text_only`: Extracts the inner text of the html DOM. Responds with text output.<br> - `input_fields`: Extracts the interactive elements in the DOM (button, input, textarea, etc.) and responds with a compact JSON object.<br> - `all_fields`: Extracts all the fields in the DOM and responds with a compact JSON object. | `enter_text_and_click` - Optimized method that combines enter text and click skills. The optimization here helps use cases such as enter text in a field and press the search button. Since the DOM would not have changed or changes should be immaterial to this action, identifying both selectors for an input field and an actionable button can happen based on the same DOM examination. |
| `get_user_input` - Provides the orchestrator with a mechanism to receive user feedback to disambiguate or seek clarity on fulfilling their request. | `bulk_enter_text` - Optimized method that wraps enter_text method so that multiple text entries can be performed one shot. |
|  | `enter_text` - Enters text in a field specified by the provided DOM query selector. |
|  | `openurl` - Opens the given URL in current or new tab. |


### DOM Distillation

Agent-E's approach to managing the vast landscape of HTML DOM is methodical and, frankly, essential for efficiency. We've introduced DOM Distillation to pare down the DOM to just the elements pertinent to the user's task.

In practice, this means taking the expansive DOM and delivering a more digestible JSON snapshot. This isn't about just reducing size, it's about honing in on relevance, serving the LLMs only what's necessary to fulfill a request. So far we have three content types:

- **Text only**: For when the mission is information retrieval, and the text is the target. No distractions.
- **Input fields**: Zeroing in on elements that call for user interaction. It’s about streamlining actions.
- **All content**: The full scope of distilled DOM, encompassing all elements when the task demands a comprehensive understanding.

It's a surgical procedure, carefully removing extraneous information while preserving the structure and content needed for the agent’s operation. Of course with any distillation there could be casualties, but the idea is to refine this over time to limit/eliminate them.

Since we can't rely on all web page authors to use best practices, such as adding unique ids to each HTML element, we had to inject our own attribute (`mmid`) in every DOM element. We can then guide the LLM to rely on using `mmid` in the generated DOM queries.

To cutdown on some of the DOM noise, we use the DOM Accessibility Tree rather than the regular HTML DOM. The accessibility tree by nature is geared towards helping screen readers, which is closer to the mission of web automation than plain old HTML DOM.

The distillation process is a work in progress. We look to refine this process and condense the DOM further aiming to make interactions faster, cost-effective, and more accurate.

## Testing and Benchmarking

Agent-E builds on the work done by [Web Arena](https://github.com/web-arena-x/webarena) for testing and evaluation. The `test` directory contains a `tasks` subdirectory with JSON files that define test cases, which also serve as examples.

Agent-E operates in a real-world web environment, which introduces variability in testing. As a result, not all tests may pass consistently due to changes in live websites. The goal is to ensure Agent-E works as expected across a wide range of tasks, with a focus on practical web automation.

### Running Tests

To run the full test suite, use the following command:

```bash
python -m test.run_tests
```

### macOS Users
If you're running the tests on macOS and encounter `BlockingIOError`, run the tests with unbuffered output:
```bash
python -u -m test.run_tests
```

### Running Specific Tests
If you want to run specific tests, you can modify the minimum and maximum task indices. This will run a subset of the tasks defined in the test configuration file.

Example:
```bash
python -m test.run_tests --min_task_index 0 --max_task_index 28 --test_results_id first_28_tests
```
This command will run tests from index 0 to 27 and assign the results the identifier `first_28_tests`.

### Parameters for run_tests
Here are additional parameters that you can pass to customize the test execution:
- `--min_task_index`: Minimum task index to start tests from (default: 0).
- `--max_task_index`: Maximum task index to end tests with, non-inclusive.
- `--test_results_id`: A unique identifier for the test results. If not provided, a timestamp is used.
- `--test_config_file`: Path to the test configuration file. Default is `test/tasks/test.json`.
- `--wait_time_non_headless`: The amount of time to wait between headless tests.
- `--take_screenshots`: Takes screenshots after every operation performed. Example: `--take_screenshots` `true`. Default is `false`

### Example Command
Here’s an example of how to use the parameters (macOS Users add `-u` parameter to the command below):
```bash
python -m test.run_tests --min_task_index 0 --max_task_index 28 --test_results_id first_28_tests
```


## Contributing

Thank you for your interest in contributing to Agent-E! We welcome contributions from the community and appreciate your help in improving the project.

### How to Contribute:

1. **Fork the Repository**  
   Start by forking the [Agent-E repository](https://github.com/EmergenceAI/Agent-E.git) to your GitHub account.

2. **Create a New Branch**  
   Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b my-feature-branch
   ```

3. **Make Changes**
Implement your changes in your new branch. Be sure to follow the project's coding style and best practices.

4. **Run Tests**
Before submitting your pull request, ensure that all tests pass by running:
```bash
python -m test.run_tests
```

5. **Submit a Pull Request**
Once your changes are ready, push your branch to your GitHub fork and submit a pull request to the main repository. Please include a clear description of your changes and why they are necessary.

### Contribution Guidelines:
- Follow the [contributing guidelines](CONTRIBUTING.md) for more detailed information on contributing.
- Be sure to write clear and concise commit messages.
- When submitting a pull request, make sure to link any related issues and provide a detailed description of the changes.


### Code of Conduct:
Please note that we have a [Code of Conduct](CODE_OF_CONDUCT.md) that all contributors are expected to follow. We are committed to providing a welcoming and inclusive environment for everyone.

### Reporting Issues:
If you encounter a bug or have a feature request, please open an issue in the [GitHub issue tracker](https://github.com/EmergenceAI/Agent-E/issues). Be sure to provide detailed information so we can address the issue effectively.

### Join the Discussion:
We encourage you to join our community on [Discord](https://discord.gg/wgNfmFuqJF) for discussions, questions, and updates on Agent-E.


## Docs Generation

Agent-E uses [Sphinx](https://www.sphinx-doc.org/en/master/) to generate its documentation. To contribute or generate documentation locally, follow these steps:

### Prerequisites

Ensure that you have installed the development dependencies before generating the docs. You can install them using the following command:

```bash
uv pip install -r pyproject.toml --extra dev
```

### Steps to Generate Documentation
1. Navigate to the project root directory:
```bash
cd Agent-E
```

2. Create a `docs` directory if it doesn’t exist:
```bash
mkdir docs
cd docs
```

3. Initialize Sphinx using the quickstart command:
```bash
sphinx-quickstart
```

4. Configure Sphinx by editing the `docs/conf.py` file. Add the following lines to include the project in the Sphinx path and enable extensions:
```python
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']
html_theme = 'sphinx_rtd_theme'
```

5. Generate API Documentation:
From the project root, run the following command to generate API documentation files:
```bash
sphinx-apidoc -o docs/source .
```

6. Build the Documentation:
After generating the API documentation, go to the `docs` directory and build the HTML docs:
```bash
sphinx-build -b html . _build
```

### Viewing the Documentation
Once the documentation is built, open the generated HTML files in your browser by navigating to the `_build` directory and opening `index.html`.
```bash
open _build/index.html
```

This will display the generated documentation in your default web browser.

## Join the Community

We encourage you to become part of the Agent-E community! Whether you're here to ask questions, share feedback, or contribute to the project, we welcome all participation.

### Join the Conversation:

- **Discord**: Connect with other users and developers in our [Discord community](https://discord.gg/wgNfmFuqJF). Feel free to ask questions, share your experiences, or discuss potential features with fellow users and contributors.

### Stay Updated:

Stay informed about new features, updates, and announcements by following the project and engaging with the community.

- **GitHub**: Keep an eye on the latest issues and pull requests, and contribute directly to the codebase on [GitHub](https://github.com/EmergenceAI/Agent-E).

We look forward to seeing you in the community!


## Citation

If you use this work in your research or projects, please cite the following article:

```
@misc{abuelsaad2024-agente,
      title={Agent-E: From Autonomous Web Navigation to Foundational Design Principles in Agentic Systems},
      author={Tamer Abuelsaad and Deepak Akkil and Prasenjit Dey and Ashish Jagmohan and Aditya Vempaty and Ravi Kokku},
      year={2024},
      eprint={2407.13032},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2407.13032},
}
```
You can also view the paper on [arXiv](https://arxiv.org/abs/2407.13032).


## TODO

Here are some features and improvements planned for future releases of Agent-E:

- **Robust Dropdown Handling**: Improve handling for dropdowns on sites like travel booking platforms (e.g., Booking.com, Expedia, Google Flights). Many of these menus have dynamic content or combine multiple aspects, such as selecting both departure and return dates within the same menu.
- **Task Caching**: Implement caching for tasks that have been run before, allowing users to rerun tasks without requiring new LLM calls. This cache should be smart, selectively caching elements like DOM locators while excluding items such as information retrieval results to improve token efficiency.
- **Open Source and Local LLM Compatibility**: Adapt Agent-E to work with open-source LLMs, ideally allowing it to run locally. This may involve simplifying prompts or refactoring skills to match the capabilities of these models.
- **Multi-Tab and Bookmark Handling**: Add skills to support bookmarks and multi-tab usage. Currently, Agent-E can handle only one tab at a time, losing state if another tab is opened, requiring the user to restart.
- **PDF Text Handling**: Enhance support for managing large amounts of text from PDFs that exceed LLM context windows, possibly by chunking the text with some overlap to retain context.
- **Browser Nav Agent History Optimization**: Improve the Browser Navigation Agent by developing ways to trim browser history, aiming to reduce token usage and cognitive load on the LLM.
- **Harvest User Preferences**: Integrate Long-Term Memory (LTM) support to automatically populate user preferences over time, with options for users to manually inject preferences. This may involve using a vector database like FAISS locally or an external hosted vector database.
- **DOM Distillation Testing Harness**: Develop a testing harness for DOM distillation, allowing distillation improvements to be measured for accuracy and performance improvements.
- **DOM Distillation Optimization**: Continue to make DOM distillation faster and more efficient.
- **Shadow DOM Support**: Some sites use Shadow DOMs, support extracting its content from Accessibility Tree.
- **Google Suite Compatibility**: Add support for Google Docs, Sheets, Slides, and Gmail, which often use canvas elements inaccessible via conventional DOM methods.
- **Cross-Platform Installer**: Create an installer compatible with Windows, Mac, and ideally Ubuntu, aimed at non-technical users. This installer should allow for environment variable configuration within the app.
- **Execution Process Video Recording**: Implement video recording to capture the execution process, as requested in issue [#106](https://github.com/EmergenceAI/Agent-E/issues/106).
- **DOM Distillation Optimizations**: Replace deprecated `snapshot()` method for DOM distillation.
- **Token Optimization**: Investigate ways to reduce the number of tokens used by the AutoGen-required prompts and annotations.
- ~~**Action Verification**: Implement response for every skill that reflects DOM changes (using Mutation Observers), so the LLM can judge if the skill executed properly.~~
- ~~**Execution Planner**: Develop a planner agent that can make the LLM decide on multiple steps ahead for faster execution.~~
- ~~[Nested chat did the trick]**Group Chat**: Enable group chat features and move some skills to different agents.~~


