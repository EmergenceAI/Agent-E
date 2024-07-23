from collections.abc import Callable
from queue import Empty
from queue import Queue


class NotificationManager:
    """
    NotificationManager handles the dispatching of notifications to registered listeners.

    Attributes:
        notification_queue (Queue): A queue to hold notifications.
        listeners (list[Callable[[dict[str, str]], None]]): A list of listener callbacks to notify.
    """

    def __init__(self):
        """
        Initialize the NotificationManager with an empty queue and no listeners.
        """
        self.notification_queue = Queue() # type: ignore
        self.listeners: list[Callable[[dict[str, str]], None]] = []

    def notify(self, message: str, message_type: str) -> None:
        """
        Notify all registered listeners with a message and its type.

        Args:
            message (str): The message to notify.
            message_type (str): The type of the message.
        """
        notification = {
            "message": message,
            "type": message_type,
        }

        if self.listeners:
            self.notification_queue.put(notification) # type: ignore
            for listener in self.listeners:
                listener(notification)
        else:
            print(f"No listeners available, discarding message: {notification}")

    def get_next_notification(self) -> dict[str, str] | None:
        """
        Get the next notification from the queue, if available.

        Returns:
            dict[str, str] | None: The next notification, or None if the queue is empty.
        """
        try:
            return self.notification_queue.get_nowait() # type: ignore
        except Empty:
            return None

    def register_listener(self, listener: Callable[[dict[str, str]], None]) -> None:
        """
        Register a new listener to receive notifications.

        Args:
            listener (Callable[[dict[str, str]], None]): The listener callback to register.
        """
        self.listeners.append(listener)

    def unregister_listener(self, listener: Callable[[dict[str, str]], None]) -> None:
        """
        Unregister a listener from receiving notifications.

        Args:
            listener (Callable[[dict[str, str]], None]): The listener callback to unregister.
        """
        self.listeners.remove(listener)
