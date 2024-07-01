import os

import anthropic
from anthropic import AsyncAnthropic
from dotenv import load_dotenv


class AnthropicLLMHelper:
    def __init__(self):
        load_dotenv()
        self.client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    async def get_chat_completion_response_async(self, system_msg:str, user_msgs:list[str], model_name:str="claude-3-opus-20240229", temperature:float=0.1, max_tokens:int=256, top_p:int=1, top_k: int=1) -> str:
        formatted_user_msgs: list[dict[str, str]] = []
        for user_msg in user_msgs:
            formatted_user_msgs.append({"type": "text", "text": user_msg})

        try:
            message = await self.client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg,
                messages=[
                    {
                        "role": "user",
                        "content": formatted_user_msgs # type: ignore

                    }
                ]
            )
            print(message)
            return message.content[0].text
        except anthropic.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
            raise Exception(f"Calling {model_name} LLM failed. The server could not be reached. Error: {e}")  # noqa: B904
        except anthropic.RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
            raise Exception(f"Calling {model_name} LLM failed. Rate limit error. Error: {e}")  # noqa: B904
        except anthropic.APIStatusError as e:
            print(e.status_code)
            print(e.response)
            raise Exception(f"Calling {model_name} LLM failed. Error: {e}")  # noqa: B904

# async def main():
#     from ae.core.prompts import LLM_PROMPTS
#     helper = AnthropicLLMHelper()
#     response = await helper.get_chat_completion_response_async(LLM_PROMPTS["SKILLS_HARVESTING_PROMPT"], ["What is the weather like today?"], temperature=0, max_tokens=4000)
#     print("*******\nResponse: ", response, "\n*******\n")

# asyncio.run(main())
