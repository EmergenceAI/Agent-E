import asyncio
import json
import logging
import os
import uuid
from queue import Empty
from queue import Queue

import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic import Field

import ae.core.playwright_manager as browserManager
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
    await browser_manager.async_initialize()


@app.post("/execute_task", description="Execute a given command related to web navigation and return the result.")
async def execute_task(request: Request, query_model: CommandQueryModel):
    notification_queue = Queue()  # type: ignore
    register_notification_listener(notification_queue)
    return StreamingResponse(run_task(query_model.command, browser_manager, notification_queue), media_type="text/event-stream")


def run_task(command: str, playwright_manager: browserManager.PlaywrightManager, notification_queue: Queue):  # type: ignore
    """
    Run the task to process the command and generate events.

    Args:
        command (str): The command to execute.
        playwright_manager (PlaywrightManager): The manager handling browser interactions and notifications.
        notification_queue (Queue): The queue to hold notifications for this request.

    Yields:
        str: JSON-encoded string representing a notification.
    """

    async def event_generator():
        # Start the process command task
        task = asyncio.create_task(process_command(command, playwright_manager))

        while not task.done() or not notification_queue.empty():
            try:
                notification = notification_queue.get_nowait()  # type: ignore
                yield f"data: {json.dumps(notification)}\n\n"  # Using 'data: ' to follow the SSE format
            except Empty:
                await asyncio.sleep(0.1)

        # Ensure the task is awaited to propagate any exceptions
        await task

    return event_generator()


async def process_command(command: str, playwright_manager: browserManager.PlaywrightManager):
    """
    Process the command and send notifications.

    Args:
        command (str): The command to process.
        playwright_manager (PlaywrightManager): The manager handling browser interactions and notifications.
    """
    current_url = await playwright_manager.get_current_url()
    await playwright_manager.notify_user("Processing command", MessageType.INFO)

    ag = await AutogenWrapper.create()
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
