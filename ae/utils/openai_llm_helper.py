import os
from typing import Any

import openai
from dotenv import load_dotenv
from openai import AsyncOpenAI


class OpenAILLMHelper:
    def __init__(self):
        load_dotenv()
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    async def get_chat_completion_response_async(self, system_msg:str, user_msgs:list[str], model_name:str="gpt-4-turbo-preview", temperature:float=0.1, max_tokens:int=256, frequency_penalty:float=0.0, top_p: float=1.0, top_k: int=1, presence_penalty: float=0.0):
        formatted_msgs: list[dict[str, Any]] = [{"role": "system", "content": system_msg}]

        for user_msg in user_msgs:
            formatted_msgs.append({"role": "user", "content": user_msg})

        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                top_p=top_p,
                presence_penalty=presence_penalty,
                messages=formatted_msgs # type: ignore
            )
            print(">>> openai response:", response)
            if response.choices and len(response.choices) > 0 and response.choices[0].message and response.choices[0].message.content:
                return response.choices[0].message.content
            return None
        except openai.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
            raise Exception(f"Calling {model_name} LLM failed. The server could not be reached.") from e
        except openai.RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
            raise Exception(f"Calling {model_name} LLM failed. Rate limit error.") from e
        except openai.APIStatusError as e:
            print(e.status_code)
            print(e.response)
            raise Exception(f"Calling {model_name} LLM failed. Error: {e}") from e

# async def main():
#     helper = OpenAILLMHelper()
#     response = await helper.get_chat_completion_response_async(LLM_PROMPTS["SKILLS_HARVESTING_PROMPT"], ["What is the weather like today?"], temperature=0, max_tokens=4000)
#     print("*******\nResponse: ", response, "\n*******\n")

# asyncio.run(main())
