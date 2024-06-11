
import inspect
from typing import Any, Dict, List, Optional, Tuple, Union
from autogen import Agent
from autogen import UserProxyAgent
import asyncio


class UserProxyAgent_SequentialFunctionExecution(UserProxyAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_reply(Agent, UserProxyAgent_SequentialFunctionExecution.sequential_generate_tool_calls_reply) # type: ignore


    def sequential_generate_tool_calls_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[Dict, None]]:
        """Generate a reply using tool call."""
        if config is None:
            config = self
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        tool_returns = []
        print("Sequential Function calling...")
        skip_flag:bool = False
        for tool_call in message.get("tool_calls", []):
            function_call = tool_call.get("function", {})
            func = self._function_map.get(function_call.get("name", None), None)
            if inspect.iscoroutinefunction(func):
                try:
                    # get the running loop if it was already created
                    loop = asyncio.get_running_loop()
                    close_loop = False
                except RuntimeError:
                    # create a loop if there is no running loop
                    loop = asyncio.new_event_loop()
                    close_loop = True
                if (not skip_flag):
                    _, func_return = loop.run_until_complete(self.a_execute_function(function_call))
                    if close_loop:
                        loop.close()
            else:
                _, func_return = self.execute_function(function_call)
            if func_return is None:
                content = "" 
            else:
                content = func_return.get("content", "")

            if content is None:
                content = ""

            if ("as a consequence of this action" in content.lower()):
                skip_flag = True
                
            tool_call_id = tool_call.get("id", None)
            if tool_call_id is not None:
                tool_call_response = {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "content": content,
                }
            else:
                tool_call_response = {
                    "role": "tool",
                    "content": content,
                }
            tool_returns.append(tool_call_response)

        if tool_returns:
            return True, {
                "role": "tool",
                "tool_responses": tool_returns,
                "content": "\n\n".join([self._str_for_tool_response(tool_return) for tool_return in tool_returns]), # type: ignore
            }
        return False, None