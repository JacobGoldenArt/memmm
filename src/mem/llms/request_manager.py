import json
import logging
from mem.llms.request import ProxyRequest
from mem.messages.messages_manager import Messages
from mem.toolkit.tools_manager import ToolsManager

logger = logging.getLogger(__name__)


class RequestManager:
    def __init__(
        self,
        messages: Messages,
        tools_manager: ToolsManager,
        proxy_request: ProxyRequest,
    ):
        """
        Manages requests to the backend API using the current chat configuration and user input.
        Args:
            messages: Handles the collection of chat messages for context.
            tools_manager: Manages tool functions that can be called within the chat.
            proxy_request: Handles the actual API requests to the language model.
        """
        self.messages = messages
        self.tools_manager = tools_manager
        self.proxy_request = proxy_request

    async def make_request(self, chat_config, user_input):
        """
        Sends a request to the backend API and processes the response.
        Args:
            chat_config: Configuration settings for the chat.
            user_input: The input message from the user.
        """
        self.messages.add_message("user", user_input)

        while True:
            response = await self.proxy_request.llm_request(
                chat_config, self.messages.messages
            )
            if response:
                return self._handle_response(response)
            else:
                logger.error("Failed to receive a valid response from the API.")
                raise ValueError("API request failed")

    def _handle_response(self, response):
        """
        Handles responses from the API, depending on the response type.
        Args:
            response: The received response from the API.
        """
        finish_reason = response.choices[0].finish_reason
        message = response.choices[0].message

        if finish_reason == "tool_calls":
            return self._execute_tool_call(message)
        elif finish_reason == "stop":
            self.messages.add_message("assistant", message.content)
            return response
        else:
            logger.error(f"Unknown finish reason: {finish_reason}")
            return None

    def _execute_tool_call(self, message):
        """
        Executes a specific tool call as requested by the backend API.
        Args:
            message: The message object containing the tool call information.
        """
        function_name = message.tool_calls[0].function.name
        function_args = json.loads(message.tool_calls[0].function.arguments)
        function_to_call = self.tools_manager.toolkit[function_name]
        function_response = await function_to_call(**function_args)

        self.messages.add_message(
            "function", f"The result of {function_name} was: {function_response}"
        )
        return function_response
