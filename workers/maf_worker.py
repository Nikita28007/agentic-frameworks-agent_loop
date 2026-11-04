"""Microsoft Agent Framework builder: works one task on the shared board.

    uv run workers/maf_worker.py <task_id> <board_path>
"""
from __future__ import annotations

import asyncio
import warnings

import common  # first project import: sets BOARD_PATH and sys.path
from common import (
    FILESYSTEM_SERVER_ARGS, INSTRUCTIONS, MODEL, WORK_DIR,
    claim, complete_task, plan_steps, show_todos, task_message,
)

warnings.filterwarnings("ignore", message=r".*experimental.*")  # quiet import-time notices

from agent_framework import Agent, MCPStdioTool  # noqa: E402
from agent_framework.openai import OpenAIChatClient  # noqa: E402


async def main() -> None:
    claim()
    filesystem = MCPStdioTool(
        name="filesystem", command="npx", args=FILESYSTEM_SERVER_ARGS, cwd=str(WORK_DIR),
    )
    async with filesystem:
        worker = Agent(
            client=OpenAIChatClient(model=MODEL),
            instructions=INSTRUCTIONS,
            tools=[show_todos, plan_steps, complete_task, filesystem],
        )
        await worker.run(task_message())


if __name__ == "__main__":
    asyncio.run(main())