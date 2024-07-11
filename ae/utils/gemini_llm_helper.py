import os
import re
from typing import Any

import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv

from ae.utils.logger import logger

GCP_BLOCK_NONE_SAFETY_SETTINGS: list[dict[str, str]] = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

# Pre-compile the regular expression pattern for removing json markers from LLM response
llm_json_or_python_begin_response_pattern = re.compile(r"^```(python|json)?\n?")
llm_end_response_pattern = re.compile(r"```$")

class GeminiLLMHelper:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY")) # type: ignore

    def process_llm_response(self, response: str):
        if response:
            # Use the compiled regex to replace the patterns with an empty string
            response = llm_json_or_python_begin_response_pattern.sub("", response)
            response = llm_end_response_pattern.sub("", response)
        return response

    async def get_chat_completion_response_async(self, system_msg:str, user_msgs:list[str], model_name:str="gemini-1.5-pro-latest", temperature:float=0.1,
                                                 max_tokens:int=256, top_p:int=1, top_k: int=1, safety_settings:list[dict[str, str]]=GCP_BLOCK_NONE_SAFETY_SETTINGS) -> str|None:
        formatted_msgs: list[dict[str, Any]] = [{"role": "user", "parts": [system_msg]}]
        user_msgs_parts: list[str] = []
        for user_msg in user_msgs:
            user_msgs_parts.append(user_msg)

        formatted_msgs.append({"role": "user", "parts": user_msgs_parts})
        response = None
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(formatted_msgs, stream=False,  # type: ignore
                                              generation_config=genai.types.GenerationConfig(
                                                  max_output_tokens=max_tokens,
                                                  temperature=temperature,
                                                  top_p=top_p,
                                                  top_k=top_k),
                                            safety_settings=safety_settings)
            return self.process_llm_response(response.text)
        except ValueError:
            if response:
                logger.error(f"Response from GCP Gen AI did not contain text. prompt: {system_msg} and user messages: {user_msgs}. Candidates: {response.candidates}")
            else:
                logger.error(f"There was no response from GCP Gen AI for prompt: {system_msg} and user messages: {user_msgs}")
            return None

# async def main():
#     from ae.core.prompts import LLM_PROMPTS
#     helper = GeminiLLMHelper()
#     response = await helper.get_chat_completion_response_async(LLM_PROMPTS["SKILLS_HARVESTING_PROMPT"], ["What is the weather like today?", "And How are you?"], temperature=0, max_tokens=4000)
#     print("*******\nResponse: ", response, "\n*******\n")

# asyncio.run(main())
