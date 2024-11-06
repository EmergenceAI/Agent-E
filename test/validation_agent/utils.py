### Subset of helper functions from eclair-agents
import base64
import sys
import time
import traceback
from typing import Any

import openai

SYSTEM_PROMPT: str = "You are a helpful assistant that automates digital workflows."


def encode_image(path_to_img: str):
    """Base64 encode an image"""
    with open(path_to_img, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def load_screenshot_for_state(state: dict[str, Any]) -> tuple[str, str]:
    path_to_screenshot: str = state["path_to_screenshot"]
    encoded_image: str = encode_image(path_to_screenshot)
    return path_to_screenshot, encoded_image


def fetch_openai_vision_completion(prompt: str, base64_images: list[str], **kwargs) -> str:
    """Helper function to call OpenAI's Vision API. Handles rate limit errors and other exceptions"""
    messages: list[Any] = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"},
                }
                for img in base64_images
            ]
            + [{"type": "text", "text": prompt}],
        },
    ]
    return _fetch_openai_completion(messages, model="gpt-4-vision-preview", **kwargs)


def _fetch_openai_completion(messages: list[Any], model: str, **kwargs) -> str:
    """Helper function to call OpenAI's Vision API. Handles rate limit errors and other exceptions"""
    client = openai.OpenAI()
    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            model=model,
            max_tokens=4096,
            **kwargs,
        )
    except openai.RateLimitError:
        print("Rate limit exceeded -- waiting 1 min before retrying")
        time.sleep(60)
        return _fetch_openai_completion(messages, model, **kwargs)
    except openai.APIError as e:
        traceback.print_exc()
        print(f"OpenAI API error: {e}")
        sys.exit(1)
    except Exception as e:
        traceback.print_exc()
        print(f"Unknown error: {e}")
        sys.exit(1)
    return response.choices[0].message.content


def build_prompt_sequence(state_seq: list[Any]) -> list[str]:
    # Loop through states
    prompt_sequence: list[str] = []
    for item in state_seq:
        path_to_screenshot, encoded_image = load_screenshot_for_state(item)
        prompt_sequence.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                    }
                ],
            }
        )
    return prompt_sequence
