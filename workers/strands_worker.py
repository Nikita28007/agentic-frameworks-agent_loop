"""Strands builder: works one task on the shared board.

    uv run workers/strands_worker.py <task_id> <board_path>
"""
from __future__ import annotations

import asyncio
import os
import subprocess

import common  # first project import: sets BOARD_PATH and sys.path
from common import (
    FILESYSTEM_SERVER_ARGS, INSTRUCTIONS, MODEL, WORK_DIR,
    claim, complete_task, plan_steps, show_todos, task_message,
)

from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient

model = OpenAIModel(client_args={"api_key": os.environ["OPENAI_API_KEY"]}, model_id=MODEL)

filesystem = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(command="npx", args=FILESYSTEM_SERVER_ARGS, cwd=str(WORK_DIR)),
        errlog=subprocess.DEVNULL,
    ),
    startup_timeout=60,
)


async def main() -> None:
    claim()
    worker = Agent(
        model=model,
        system_prompt=INSTRUCTIONS,
        tools=[tool(show_todos), tool(plan_steps), tool(complete_task), filesystem],
    )
    await worker.invoke_async(task_message())


if __name__ == "__main__":
    asyncio.run(main())