"""Agno builder: works one task on the shared board.

    uv run workers/agno_worker.py <task_id> <board_path>
"""
from __future__ import annotations

import asyncio

import common  # first project import: sets BOARD_PATH and sys.path
from common import (
    FILESYSTEM_SERVER_ARGS, INSTRUCTIONS, MODEL, WORK_DIR,
    claim, complete_task, plan_steps, show_todos, task_message,
)


from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters


async def main() -> None:
    claim()
    server = StdioServerParameters(command="npx", args=FILESYSTEM_SERVER_ARGS, cwd=str(WORK_DIR))
    async with MCPTools(server_params=server, timeout_seconds=60) as filesystem:
        worker = Agent(
            model=OpenAIChat(id=MODEL),
            instructions=INSTRUCTIONS,
            tools=[show_todos, plan_steps, complete_task, filesystem],
        )
        await worker.arun(input=task_message())


if __name__ == "__main__":
    asyncio.run(main())