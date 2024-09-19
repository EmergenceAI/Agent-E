
import asyncio
import inspect
from typing import Any

from autogen import Agent  # type: ignore
from autogen import UserProxyAgent  # type: ignore


class UserProxyAgent_SequentialFunctionExecution(UserProxyAgent):
    def __init__(self, *args, **kwargs): # type: ignore
        super().__init__(*args, **kwargs) # type: ignore
        #position = 2 allows termination check to be called earlier, this helps detect loops.
        self.register_reply(Agent, UserProxyAgent_SequentialFunctionExecution.sequential_generate_tool_calls_reply, position=2) # type: ignore


    def sequential_generate_tool_calls_reply( # type: ignore
        self,
        messages: list[dict] | None = None, # type: ignore
        sender: Agent | None = None,
        config: Any | None = None,
    ) -> tuple[bool, dict[str, Any] | None]:
        """Generate a reply using tool call."""
        if config is None:
            config = self
        if messages is None:
            messages = self._oai_messages[sender] # type: ignore
        message = messages[-1] # type: ignore
        tool_returns = []
        skip_flag:bool = False
        for tool_call in message.get("tool_calls", []): # type: ignore
            function_call = tool_call.get("function", {}) # type: ignore
            func = self._function_map.get(function_call.get("name", None), None) # type: ignore
            func_return = None
            if inspect.iscoroutinefunction(func): # type: ignore
                try:
                    # get the running loop if it was already created
                    loop = asyncio.get_running_loop()
                    close_loop = False
                except RuntimeError:
                    # create a loop if there is no running loop
                    loop = asyncio.new_event_loop()
                    close_loop = True
                if (not skip_flag):
                    _, func_return = loop.run_until_complete(self.a_execute_function(function_call)) # type: ignore
                    if close_loop:
                        loop.close()
            else:
                if (not skip_flag):
                    _, func_return = self.execute_function(function_call) # type: ignore
            if func_return is None: # type: ignore
                if skip_flag:
                    content = "VERY IMPORTANT: This function could not be executed since previous function resulted in a Webpage change. You must get all_fields DOM and repeat the function if needed."
                else:
                    content = ""
            else:
                content = func_return.get("content", "") # type: ignore

            if content is None:
                content = ""

            if ("as a consequence of this action" in content.lower()): # type: ignore
                skip_flag = True

            tool_call_id = tool_call.get("id", None) # type: ignore
            if tool_call_id is not None:
                tool_call_response = { # type: ignore
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "content": content,
                }
            else:
                tool_call_response = { # type: ignore
                    "role": "tool",
                    "content": content,
                }
            tool_returns.append(tool_call_response) # type: ignore

        if tool_returns:
            return True, {
                "role": "tool",
                "tool_responses": tool_returns,
                "content": "\n\n".join([self._str_for_tool_response(tool_return) for tool_return in tool_returns]), # type: ignore
            }
        return False, None
