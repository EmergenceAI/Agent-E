import asyncio
import json
import logging
import os
import uuid
from queue import Empty
from queue import Queue
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic import Field

import ae.core.playwright_manager as browserManager
from ae.core.agents_llm_config import AgentsLLMConfig
from ae.core.autogen_wrapper import AutogenWrapper
from ae.utils.ui_messagetype import MessageType

browser_manager = browserManager.PlaywrightManager(headless=False)

APP_VERSION = "1.0.0"
APP_NAME = "Agent-E Web API"
API_PREFIX = "/api"
IS_DEBUG = False
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))
WORKERS = 1

container_id = os.getenv("CONTAINER_ID", "")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("uvicorn")


class CommandQueryModel(BaseModel):
    command: str = Field(..., description="The command related to web navigation to execute.")  # Required field with description
    llm_config: dict[str,Any] | None = Field(None, description="The LLM configuration string to use for the agents.")
    clientid: str | None = Field(None, description="Client identifier, optional")
    request_originator: str | None = Field(None, description="Optional id of the request originator")


def get_app() -> FastAPI:
    """Starts the Application"""
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    fast_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    return fast_app


app = get_app()


@app.on_event("startup")  # type: ignore
async def startup_event():
    """
    Startup event handler to initialize browser manager asynchronously.
    """
    global container_id

    if container_id.strip() == "":
        container_id = str(uuid.uuid4())
        os.environ["CONTAINER_ID"] = container_id
    await browser_manager.async_initialize()


@app.post("/execute_task", description="Execute a given command related to web navigation and return the result.")
async def execute_task(request: Request, query_model: CommandQueryModel):
    notification_queue = Queue()  # type: ignore
    transaction_id = str(uuid.uuid4()) if query_model.clientid is None else query_model.clientid
    register_notification_listener(notification_queue)
    return StreamingResponse(run_task(request, transaction_id, query_model.command, browser_manager, notification_queue, query_model.request_originator, query_model.llm_config), media_type="text/event-stream")


def run_task(request: Request, transaction_id: str, command: str, playwright_manager: browserManager.PlaywrightManager, notification_queue: Queue, request_originator: str|None = None, llm_config: dict[str,Any]|None = None):  # type: ignore
    """
    Run the task to process the command and generate events.

    Args:
        request (Request): The request object to detect client disconnect.
        transaction_id (str): The transaction ID to identify the request.
        command (str): The command to execute.
        playwright_manager (PlaywrightManager): The manager handling browser interactions and notifications.
        notification_queue (Queue): The queue to hold notifications for this request.
        request_originator (str|None): The originator of the request.

    Yields:
        str: JSON-encoded string representing a notification.
    """

    async def event_generator():
        task = asyncio.create_task(process_command(command, playwright_manager, llm_config))
        task_detail = f"transaction_id={transaction_id}, request_originator={request_originator}, command={command}"

        try:
            while not task.done() or not notification_queue.empty():
                if await request.is_disconnected():
                    logger.info(f"Client disconnected. Cancelling the task: {task_detail}")
                    task.cancel()
                    break
                try:
                    notification = notification_queue.get_nowait()  # type: ignore
                    notification["transaction_id"] = transaction_id  # Include the transaction ID in the notification
                    notification["request_originator"] = request_originator  # Include the request originator in the notification
                    yield f"data: {json.dumps(notification)}\n\n"  # Using 'data: ' to follow the SSE format
                except Empty:
                    await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    logger.info(f"Task was cancelled due to client disconnection. {task_detail}")
                except Exception as e:
                    logger.error(f"An error occurred while processing task: {task_detail}. Error: {e}")

            await task
        except asyncio.CancelledError:
            logger.info(f"Task was cancelled due to client disconnection. {task_detail}")
            await task

    return event_generator()



async def process_command(command: str, playwright_manager: browserManager.PlaywrightManager, llm_config:dict[str,Any]|None = None):
    """
    Process the command and send notifications.

    Args:
        command (str): The command to process.
        playwright_manager (PlaywrightManager): The manager handling browser interactions and notifications.
    """
    await playwright_manager.go_to_homepage() # Go to the homepage before processing the command
    current_url = await playwright_manager.get_current_url()
    await playwright_manager.notify_user("Processing command", MessageType.INFO)

    # Load the configuration using AgentsLLMConfig
    normalized_llm_config = None
    if llm_config is None:
        normalized_llm_config = AgentsLLMConfig()
    else:
        normalized_llm_config = AgentsLLMConfig(llm_config=llm_config)
        logger.info("Applied LLM config received via API.")

    # Retrieve planner agent and browser nav agent configurations
    planner_agent_config = normalized_llm_config.get_planner_agent_config()
    browser_nav_agent_config = normalized_llm_config.get_browser_nav_agent_config()

    ag = await AutogenWrapper.create(planner_agent_config, browser_nav_agent_config)
    command_exec_result = await ag.process_command(command, current_url)  # type: ignore

    # Notify about the completion of the command
    await playwright_manager.notify_user("DONE", MessageType.DONE)


def register_notification_listener(notification_queue: Queue):  # type: ignore
    """
    Register the event generator as a listener in the NotificationManager.
    """

    def listener(notification: dict[str, str]) -> None:
        notification["container_id"] = container_id  # Include the container ID (or UUID) in the notification
        notification_queue.put(notification)  # type: ignore

    browser_manager.notification_manager.register_listener(listener)


if __name__ == "__main__":
    logger.info("**********Application Started**********")
    uvicorn.run("main:app", host=HOST, port=PORT, workers=WORKERS, reload=IS_DEBUG, log_level="info")
