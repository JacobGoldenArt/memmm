import logging
from datetime import datetime as dt
import json

from jinja2 import Template

logger = logging.getLogger(__name__)

Default_System_Template = Template(
    """
    You are a helpful assistant named Em. Please address the user as: Jacob.
    You have access to some tools. Please use them if you need to look up
    something like Jacob's current Location or the Weather. The current date/time
    is: {{ timestamp }}.
"""
)


class Messages:
    def __init__(self):
        """
        Manages a list of messages within the chat application, providing capabilities for real-time updates and modifications.
        """
        self.messages = []

        self.subscribers = []

    def add_system_message(self):
        """
        Adds a system message to the list with metadata and notifies subscribers of the addition.
        """
        system_message = {
            "role": "system",
            "content": Default_System_Template.render(
                timestamp=dt.now().isoformat()
            ).strip(),
        }
        self.messages.append(system_message)

    def add_message(self, role, content, name=None):
        """
        Adds a message to the list with metadata and notifies subscribers of the addition.
        Args:
            role: The role of the message sender ('user' or 'assistant').
            content: The text content of the message.
            name: Optional. A name associated with the message.
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "name": name,
        }
        self.messages.append(message)
        self.notify_subscribers("add", message)

    def modify_message(self, index, new_content):
        """
        Modifies the content of an existing message by index and notifies subscribers.
        Args:
            index: The index of the message to modify.
            new_content: The new content to replace the existing message content.
        """
        if 0 <= index < len(self.messages):
            self.messages[index]["content"] = new_content
            self.notify_subscribers("modify", self.messages[index])

    def delete_message(self, index):
        """
        Deletes a message from the list by index and notifies subscribers.
        Args:
            index: The index of the message to delete.
        """
        if 0 <= index < len(self.messages):
            removed_message = self.messages.pop(index)
            self.notify_subscribers("delete", removed_message)

    def get_messages(self):
        """
        Returns a JSON string of all messages, typically used for saving or logging purposes.
        """
        return json.dumps(self.messages, indent=2)

    def notify_subscribers(self, event_type, message):
        """
        Notifies all subscribed observers about message events.
        Args:
            event_type: The type of event ('add', 'modify', 'delete').
            message: The message associated with the event.
        """
        for subscriber in self.subscribers:
            subscriber.update(event_type, message)

    def subscribe(self, observer):
        """
        Subscribes an observer to receive updates on message events.
        Args:
            observer: The observer to subscribe.
        """
        self.subscribers.append(observer)

    def unsubscribe(self, observer):
        """
        Unsubscribes an observer from receiving updates on message events.
        Args:
            observer: The observer to unsubscribe.
        """
        self.subscribers.remove(observer)


class MemoryManager:
    def __init__(self, message_manager):
        """
        Initializes a MemoryManager that works closely with Messages to manage and process message data.
        Args:
            message_manager: The associated Messages instance.
        """
        self.message_manager = message_manager
        self.message_manager.subscribe(self)

    def update(self, event_type, message):
        """
        Handles updates from the Messages instance, processing new, modified, or deleted messages.
        Args:
            event_type: The type of message event ('add', 'modify', 'delete').
            message: The message involved in the event.
        """
        if event_type == "add":
            self.process_new_message(message)

    def process_new_message(self, message):
        """
        Processes a new message, typically involves analyzing or storing message data.
        Args:
            message: The new message to process.
        """
        pass
