import autogen  # type: ignore

from ae.core.prompts import LLM_PROMPTS


class BrowserNavAgentNoSkills:
    def __init__(self, config_list, user_proxy_agent: autogen.UserProxyAgent): # type: ignore
        """
        Initialize the BrowserNavAgentNoSkills class and registers any necessary skills.

        Parameters:
        - config_list (list): Configuration parameters required for AssistantAgent.
        - user_proxy_agent (UserProxyAgent): An instance of the UserProxyAgent class.

        Returns:
        None
        """
        self.user_proxy_agent = user_proxy_agent
        self.agent = autogen.AssistantAgent(
            name="browser_navigation_agent_no_skills",
            system_message=LLM_PROMPTS["BROWSER_AGENT_NO_SKILLS_PROMPT"],
            llm_config={
                "config_list": config_list,
                "cache_seed": 41,
                "temperature": 0.0
            },
        )
        self.__register_skills()


    def __register_skills(self):
        """
        Register all the skills that the agent can perform.

        Parameters:
        None

        Returns:
        None
        """
        pass
