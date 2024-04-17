import logging

from openai import AsyncOpenAI

from mem.toolkit.tools_manager import ToolsManager

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key="anything", base_url="http://0.0.0.0:4000")


class ProxyRequest:
    tools: ToolsManager

    def __init__(self):
        self.tools = ToolsManager()

    try:

        async def llm_request(self, chat_config, messages):
            alias = chat_config.get("model")

            response = await client.chat.completions.create(
                model=alias,
                messages=messages,
                temperature=chat_config.get("temperature"),
                tools=self.tools.available_tools(),
                tool_choice="auto",
            )

            return response

    except Exception as e:
        logger.error(f"Error making request: {e}")
