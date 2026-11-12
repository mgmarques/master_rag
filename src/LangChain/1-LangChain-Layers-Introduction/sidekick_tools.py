"""
Tools for the Sidekick: a mix of MCP servers, ready-made LangChain tools and our own.

 - a headed browser
 - a sandbox filesystem through persistent MCP sessions
 - a web search
 - Wikipedia
 - push notifications
 -`request_human_help`.
"""

import asyncio
import os
import warnings

warnings.filterwarnings("ignore", message=".*langchain.mcp.*is in beta.*")

import requests
import wikipedia
from dotenv import load_dotenv
from langchain_community.tools import GoogleSerperRun, WikipediaQueryRun
from langchain_community.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
from langchain_core.tools import tool
from langchain.mcp import MCPAdapter


load_dotenv(override=True)
NTFY_TOPIC_URL = os.getenv("NTFY_TOPIC_URL", "")

# Wikimedia rejects the wikipedia library's default user agent, so identify ourselves properly
wikipedia.set_user_agent("agentic-track-course (https://edwarddonner.com)")

search = GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())

wikipedia_lookup = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())


@tool
def send_push_notification(text: str) -> str:
    """Send a short push notification to the user's phone."""
    requests.post(
        NTFY_TOPIC_URL,
        data=text.encode(encoding='utf-8')
    )
    return "Notification sent"


@tool
def request_human_help(instructions: str) -> str:
    """Ask the user to do something in the browser window that you cannot do yourself,
    such as logging in to a site, passing a captcha, or approving two-factor authentication.
    Explain exactly what you need them to do. The run pauses until they have done it."""
    return "The user says it is done. Continue with the task."


def mcp_connections(sandbox: str) -> dict:
    """
    The MCP servers the Sidekick uses: a headed browser and a sandbox filesystem.

    If you prefer to use Playwright instead of dev-browser, replace it with the Playwright setting below:
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest", "--isolated"],
        },
    """

    return {
        "dev-browser": {
            "command": "dev-browser",
            "args": ["mcp"]
        },
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox],
        },
    }


class McpSessions:
    """Holds persistent MCP sessions open so the browser keeps its state between tool calls.

    The stdio transport must be opened and closed from the same asyncio task, so one
    background task owns the sessions: it opens them, waits, and unwinds them when stop()
    is called. Stopping shuts down the servers, and you will see the browser close.
    """

    def __init__(self, connections: dict):
        self.connections = connections
        self.tools = []
        self._ready = asyncio.Event()
        self._stop = asyncio.Event()
        self._task = None

    async def _run(self):
        config = {"mcpServers": self.connections}
        async with MCPAdapter(config) as adapter:
            self.tools += await adapter.list_tools()
            self._ready.set()
            await self._stop.wait()

    async def start(self) -> list:
        self._task = asyncio.create_task(self._run())
        ready = asyncio.create_task(self._ready.wait())
        await asyncio.wait([ready, self._task], return_when=asyncio.FIRST_COMPLETED)
        ready.cancel()
        if self._task.done():
            self._task.result()  # the servers failed to start; raise the real error
        return self.tools

    def stop(self):
        self._stop.set()


async def get_all_tools(sandbox: str):
    """Return the full tool list (our tools plus the MCP server tools) and the session holder."""
    sessions = McpSessions(mcp_connections(sandbox))
    mcp_tools = await sessions.start()
    our_tools = [search, send_push_notification, wikipedia_lookup, request_human_help]
    return our_tools + mcp_tools, sessions
