import json
import os
import tempfile
import traceback
from string import Template
import autogen  # type: ignore
import openai
from autogen import GroupChat  
from autogen import Agent  
#from autogen import Cache
from dotenv import load_dotenv
from ae.core.agents.browser_nav_agent import BrowserNavAgent
from ae.core.agents.browser_nav_agent_no_skills import BrowserNavAgentNoSkills
from ae.core.agents.high_level_planner_agent import PlannerAgent
from ae.core.agents.task_verification_agent import VerificationAgent    
from ae.core.prompts import LLM_PROMPTS
from ae.utils.logger import logger


class AutogenWrapper:
    """
    A wrapper class for interacting with the Autogen library.

    Args:
        max_chat_round (int): The maximum number of chat rounds.

    Attributes:
        number_of_rounds (int): The maximum number of chat rounds.
        agents_map (dict): A dictionary of the agents that are instantiated in this autogen instance.

    """

    def __init__(self, max_chat_round: int = 50):
        self.number_of_rounds = max_chat_round
        self.group_chat_manager: autogen.GroupChatManager | None = None
        self.agents_map: dict[str, autogen.UserProxyAgent | autogen.AssistantAgent | autogen.ConversableAgent ] | None = None
        self.config_list: list[dict[str, str]] | None = None

    @classmethod
    async def create(cls, agents_needed: list[str] | None = None, max_chat_round: int = 50):
        """
        Create an instance of AutogenWrapper.

        Args:
            agents_needed (list[str], optional): The list of agents needed. If None, then ["user_proxy", "browser_nav_agent"] will be used.
            max_chat_round (int, optional): The maximum number of chat rounds. Defaults to 50.

        Returns:
            AutogenWrapper: An instance of AutogenWrapper.

        """
        if agents_needed is None:
            agents_needed = ["user_proxy", "browser_nav_agent", "planner_agent", "verification_agent"]
        # Create an instance of cls
        self = cls(max_chat_round)
        load_dotenv()
        os.environ["AUTOGEN_USE_DOCKER"] = "False"
        env_var = [{'model': 'gpt-4-turbo-preview', 'api_key': os.environ['OPENAI_API_KEY']}]
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp:
            json.dump(env_var, temp)
            temp_file_path = temp.name

        self.config_list = autogen.config_list_from_json(env_or_file=temp_file_path, filter_dict={"model": {"gpt-4-turbo-preview"}}) # type: ignore
        print()
        self.agents_map = await self.__initialize_agents(agents_needed)
        agents_for_groupchat = [agent for agent in self.agents_map.values()]
        group_chat = GroupChat(
            agents=agents_for_groupchat, # type: ignore
            messages=[],
            speaker_selection_method=self.custom_speaker_selection_func, # type: ignore
        )
        self.group_chat_manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=self.config_list[0], # type: ignore
            code_execution_config=False,
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().upper().endswith("##TERMINATE##"), # type: ignore 
        )

        return self


    async def __initialize_agents(self, agents_needed: list[str]):
        """
        Instantiate all agents with their appropriate prompts/skills.

        Args:
            agents_needed (list[str]): The list of agents needed, this list must have user_proxy in it or an error will be generated.

        Returns:
            dict: A dictionary of agent instances.

        """
        if "user_proxy" not in agents_needed:
            raise ValueError("user_proxy agent is required in the list of needed agents.")

        agents_map: dict[str, autogen.AssistantAgent | autogen.UserProxyAgent  | autogen.ConversableAgent]= {}

        user_proxy_agent = await self.__create_user_proxy_agent()
        user_proxy_agent.reset()
        agents_map["user_proxy"] = user_proxy_agent
        agents_needed.remove("user_proxy")

        for agent_needed in agents_needed:
            if agent_needed == "browser_nav_agent":
                browser_nav_agent: autogen.AssistantAgent = self.__create_browser_nav_agent(user_proxy_agent)
                browser_nav_agent.reset()
                agents_map["browser_nav_agent"] = browser_nav_agent
            elif agent_needed == "browser_nav_agent_no_skills":
                browser_nav_agent_no_skills = self.__create_browser_nav_agent_no_skills(user_proxy_agent)
                browser_nav_agent_no_skills.reset()
                agents_map["browser_nav_agent_no_skills"] = browser_nav_agent_no_skills
            elif agent_needed == "planner_agent":
                planner_agent = self.__create_planner_agent()
                planner_agent.reset()
                agents_map["planner_agent"] = planner_agent
            elif agent_needed == "verification_agent":
                verification_agent = self.__create_verification_agent()
                verification_agent.reset()
                agents_map["verification_agent"] = verification_agent
            else:
                raise ValueError(f"Unknown agent type: {agent_needed}")


        return agents_map


    async def __create_user_proxy_agent(self):
        """
        Create a UserProxyAgent instance.

        Returns:
            autogen.UserProxyAgent: An instance of UserProxyAgent.

        """
        user_proxy_agent = autogen.UserProxyAgent(
            name="user_proxy",
            system_message=LLM_PROMPTS["USER_AGENT_PROMPT"],
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().upper().endswith("##TERMINATE##"), # type: ignore
            human_input_mode="NEVER",
            max_consecutive_auto_reply=self.number_of_rounds,
            code_execution_config={
                "last_n_messages": 1,
                "work_dir": "./",
                "use_docker": False,
            }
        )

        return user_proxy_agent

    def __create_browser_nav_agent(self, user_proxy_agent: autogen.UserProxyAgent) -> autogen.AssistantAgent:
        """
        Create a BrowserNavAgent instance.

        Args:
            user_proxy_agent (autogen.UserProxyAgent): The instance of UserProxyAgent that was created.

        Returns:
            autogen.AssistantAgent: An instance of BrowserNavAgent.

        """
        browser_nav_agent = BrowserNavAgent(self.config_list, user_proxy_agent) # type: ignore
        #print(">>> browser agent tools:", json.dumps(browser_nav_agent.agent.llm_config.get("tools"), indent=2))
        return browser_nav_agent.agent


    def __create_browser_nav_agent_no_skills(self, user_proxy_agent: autogen.UserProxyAgent):
        """
        Create a BrowserNavAgentNoSkills instance. This is mainly used for exploration at this point

        Args:
            user_proxy_agent (autogen.UserProxyAgent): The instance of UserProxyAgent that was created.

        Returns:
            autogen.AssistantAgent: An instance of BrowserNavAgentNoSkills.

        """
        browser_nav_agent_no_skills = BrowserNavAgentNoSkills(self.config_list, user_proxy_agent) # type: ignore
        return browser_nav_agent_no_skills.agent

    def __create_planner_agent(self):
        """
        Create a Planner Agent instance. This is mainly used for exploration at this point

        Returns:
            autogen.AssistantAgent: An instance of PlannerAgent.

        """
        planner_agent = PlannerAgent(self.config_list) # type: ignore
        return planner_agent.agent

    def __create_verification_agent(self):
        """
        Create a Verification Agent instance. This is mainly used for exploration at this point

        Returns:
            autogen.AssistantAgent: An instance of VerificationAgent.

        """
        verification_agent = VerificationAgent(self.config_list) # type: ignore
        return verification_agent.agent

    async def process_command(self, command: str, current_url: str | None = None):
        """
        Process a command by sending it to one or more agents.

        Args:
            command (str): The command to be processed.
            current_url (str, optional): The current URL of the browser. Defaults to None.

        """
        current_url_prompt_segment = ""
        if current_url:
            current_url_prompt_segment = f"Current URL: {current_url}"

        prompt = Template(LLM_PROMPTS["COMMAND_EXECUTION_PROMPT"]).substitute(command=command, current_url_prompt_segment=current_url_prompt_segment)
        logger.info(f"Prompt for command: {prompt}")
        #with Cache.disk() as cache:
        try:
            if self.agents_map is None:
                raise ValueError("Agents map is not initialized.")
            print(f">>> agents_map: {self.agents_map}") 
            await self.agents_map["user_proxy"].a_initiate_chat( # type: ignore
                self.group_chat_manager, # self.manager # type: ignore
                #clear_history=True,
                message=prompt,
                silent=False,
                cache=None,
            )
        except openai.BadRequestError as bre:
            logger.error(f"Unable to process command: \"{command}\". {bre}")
            traceback.print_exc()


    def custom_speaker_selection_func(self, last_speaker: Agent, groupchat: autogen.GroupChat):
        """Defines a customized speaker selection function.
        A recommended way is to define a transition for each speaker in the groupchat.

        Returns:
            Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
        """
        print(f">>> last_speaker: {last_speaker}")
        return self.agents_map["browser_nav_agent"] # type: ignore
    
