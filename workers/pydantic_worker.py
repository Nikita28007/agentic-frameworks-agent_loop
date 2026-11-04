"""Pydantic AI builder: works one task on the shared board.

    uv run workers/pydantic_worker.py <task_id> <board_path>
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import common  # first project import: sets BOARD_PATH and sys.path
from common import (
    FILESYSTEM_SERVER_ARGS, INSTRUCTIONS, MODEL, WORK_DIR,
    claim, complete_task, plan_steps, show_todos, task_message,
)

from fastmcp.client.transports import StdioTransport
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

filesystem = MCPToolset(
    StdioTransport(
        command="npx",
        args=FILESYSTEM_SERVER_ARGS,
        cwd=str(WORK_DIR),
        log_file=Path(os.devnull),
    ),
    init_timeout=60,
)


async def main() -> None:
    claim()
    worker = Agent(
        f"openai-chat:{MODEL}",
        instructions=INSTRUCTIONS,
        tools=[show_todos, plan_steps, complete_task],
        toolsets=[filesystem],
    )
    async with worker:
        await worker.run(task_message())


if __name__ == "__main__":
    asyncio.run(main())