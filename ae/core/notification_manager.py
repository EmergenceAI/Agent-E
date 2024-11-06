from collections.abc import Callable


class NotificationManager:
    """
    NotificationManager handles the dispatching of notifications to registered listeners.

    Attributes:
        listeners (list[Callable[[dict[str, str]], None]]): A list of listener callbacks to notify.
    """

    def __init__(self):
        """
        Initialize the NotificationManager with no listeners.
        """
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
            for listener in self.listeners:
                listener(notification)
        else:
            print(f"No listeners available, discarding message: {notification}")

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
