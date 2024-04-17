import asyncio
import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


class TavilySearchTool:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    async def agent_search(self, query, **args):
        """Get the user's location based on their IP address."""
        response = await self.client.search(query=query, **args)
        # Get the search results as context to pass an LLM:
        context = [
            {"url": obj["url"], "content": obj["content"]} for obj in response.results
        ]
        return context

    async def get_answer(self, query):
        response = await self.client.qna_search(query=query)
        return response


if __name__ == "__main__":
    search = TavilySearchTool()
    results = asyncio.run(
        search.get_answer("What's the secret to authentic Indian Food?")
    )
    print(results)
