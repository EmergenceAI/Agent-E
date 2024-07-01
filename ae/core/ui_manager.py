
import json
import os
import traceback

from playwright.async_api import Frame
from playwright.async_api import Page

from ae.config import PROJECT_SOURCE_ROOT
from ae.utils.js_helper import escape_js_message
from ae.utils.logger import logger


class UIManager:
    """
    Manages the UI overlay for this application. The application uses playwright for the browser driver.
    This includes handling navigation events, showing or hiding overlays, and maintaining
    a conversation history within the UI overlay.

    Attributes:
        overlay_is_collapsed (bool): Indicates if the overlay is currently collapsed.
        conversation_history (list[dict[str, str]]): The chat history between user and system. Each entry contains 'from' and 'message' keys.
        __update_overlay_chat_history_running (bool): A flag to prevent concurrent updates to the chat history.
    """

    overlay_is_collapsed: bool = True
    conversation_history:list[dict[str, str]] = []
    __update_overlay_chat_history_running: bool = False


    def __init__(self):
        """
        Initializes the UIManager instance by adding default system messages to the conversation history.
        """
        self.add_default_system_messages()


    async def handle_navigation(self, frame: Frame):
        """
        Handles navigation events by injecting JavaScript code into the frame to manage the overlay state
        and updating the overlay chat history.

        Args:
            frame (Frame): The Playwright Frame object to inject JavaScript into and manage.
        """
        try:
            await frame.wait_for_load_state("load")
            overlay_injection_file = os.path.join(PROJECT_SOURCE_ROOT, "ui", "injectOverlay.js")
            with open(overlay_injection_file, 'r') as file:  # noqa: UP015
                js_code = file.read()

            # Inject the JavaScript code into the page
            await frame.evaluate(js_code)
            if self.overlay_is_collapsed:
                await frame.evaluate("showCollapsedOverlay();")
            else:
                await frame.evaluate("showExpandedOverlay();")
            #update chat history in the overlay
            await self.update_overlay_chat_history(frame)

        except Exception as e:
            if "Frame was detached" not in str(e):
                raise e


    async def show_overlay(self, page: Page):
        """
        Displays the overlay in an expanded state on the given page if it's currently collapsed.

        Args:
            page (Page): The Playwright Page object on which to show the overlay.
        """
        if not self.overlay_is_collapsed:
            logger.debug("Overlay is already expanded, ignoring show_overlay call")
            return
        await page.evaluate("showExpandedOverlay();")
        self.overlay_is_collapsed = True


    def update_overlay_state(self, is_collapsed: bool):
        """
        Updates the state of the overlay to either collapsed or expanded.

        Args:
            is_collapsed (bool): True to collapse the overlay, False to expand it.
        """
        self.overlay_is_collapsed = is_collapsed


        
    async def update_overlay_chat_history(self, frame_or_page: Frame | Page):
        """
        Updates the chat history in the overlay. If the overlay is expanded and not currently being updated,
        it clears existing messages and adds them fresh from the conversation history.

        Args:
            frame_or_page (Frame | Page): The Playwright Frame or Page object to update the chat history in.
        """
        logger.debug("Updating overlay chat history")

        if self.overlay_is_collapsed:
            logger.debug("Overlay is collapsed, not updating chat history")
            return
        if self.__update_overlay_chat_history_running:
            logger.debug("update_overlay_chat_history is already running, returning" + frame_or_page.url)
            return

        self.__update_overlay_chat_history_running = True
        #update chat history in the overlay by removing all messages and adding them again fresh
        try:
            await frame_or_page.evaluate("clearOverlayMessages();")
            for message in self.conversation_history:
                safe_message = escape_js_message(message["message"])
                if message["from"] == "user":
                    await frame_or_page.evaluate(f"addUserMessage({safe_message});")
                else:
                    await frame_or_page.evaluate(f"addSystemMessage({safe_message});")
            logger.debug("Chat history updated in overlay, removing update lock flag")
        except Exception:
            traceback.print_exc()
        finally:
            self.__update_overlay_chat_history_running = False
  

    def get_conversation_history(self):
        """
        Returns the current conversation history.

        Returns:
            list[dict[str, str]]: The conversation history.
        """
        return self.conversation_history


    def new_user_message(self, message: str):
        """
        Adds a new user message to the conversation history.

        Args:
            message (str): The message text to add.
        """
        self.conversation_history.append({"from":"user", "message":message})


    def new_system_message(self, message: str):
        """
        Adds a new system message to the conversation history.

        Args:
            message (str): The message text to add.
        """
        self.conversation_history.append({"from":"system", "message":message})


    def add_default_system_messages(self):
        """
        Adds default system messages to the conversation history to greet the user or provide initial instructions.
        """
        self.new_system_message(json.dumps("Agent-E at your service, what can I do for you?"))


    async def command_completed(self, page: Page, command: str, elapsed_time: float|None = None):
        """
        Handles the completion of a command, focusing on the overlay input and indicating that the command has finished.

        Args:
            page (Page): The Playwright Page object where the command was executed.
            command (str): The command that was completed.
            elapsed_time (float | None, optional): The time taken to complete the command, if relevant.
        """
        if not self.overlay_is_collapsed:
            await page.evaluate("focusOnOverlayInput();")
            await page.evaluate("commandExecutionCompleted();")
