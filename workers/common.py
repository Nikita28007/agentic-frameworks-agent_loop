"""Shared bootstrap for every builder: argv, board path, repo-root import, board tools.

Importing this module must be the first project import in a worker, because it sets
BOARD_PATH and sys.path before board.py is imported (board.py reads the path at import).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root, where board.py lives

if len(sys.argv) < 3:
    sys.exit(f"usage: {Path(sys.argv[0]).name} <task_id> <board_path>")

TASK_ID = int(sys.argv[1])
BOARD_PATH = Path(sys.argv[2]).resolve()
os.environ["BOARD_PATH"] = str(BOARD_PATH)
sys.path.insert(0, str(ROOT))

import board  # noqa: E402

from dotenv import load_dotenv  # noqa: E402

load_dotenv(override=True)  # find_dotenv walks up from this file, so the repo-root .env is found

MODEL = os.environ.get("WORKER_MODEL", "gpt-5.4-mini")
WORK_DIR = BOARD_PATH.parent  # the shared site folder: the only place the file tools may write
FILESYSTEM_SERVER_ARGS = ["-y", "@modelcontextprotocol/server-filesystem", str(WORK_DIR)]

INSTRUCTIONS = """
You are a careful worker with a shared todo board and a set of file tools.

Take the pending goal and see it through. Begin by laying out a short plan: the handful of concrete steps the work itself breaks down into, added to the board under the goal. Then carry them out with your file tools, marking each step done as you finish it. Once the steps are all done, close the goal. Your files live in the single folder your tools are allowed to use.
"""


def claim() -> None:
    """Light up this worker's task on the shared board (pending -> in_progress)."""
    board.claim_todo(TASK_ID)


def task_message() -> str:
    return (
        f"You have claimed task #{TASK_ID} on the shared board. Work only that task and its steps. "
        f"When the work is built and checked, mark task #{TASK_ID} itself done with complete_task, then stop."
    )


def show_todos() -> list[dict]:
    """List every todo on the board. A goal has parent_id None; a step has parent_id set to its goal's id."""
    return board.list_todos()


def plan_steps(goal_id: int, steps: list[str]) -> dict:
    """Break a goal into an ordered checklist of steps on the board.

    Args:
        goal_id: The id of the goal to break down.
        steps: Short descriptions of the steps to take, in order.
    """
    return {"goal_id": goal_id, "step_ids": [board.add_step(goal_id, s) for s in steps]}


def complete_task(task_id: int, result: str) -> dict:
    """Mark a todo (a step or the goal) done and record a short result summary.

    Args:
        task_id: The id of the todo to mark done.
        result: A short summary of what was accomplished.
    """
    board.complete_todo(task_id, result)
    return {"task_id": task_id, "status": "done"}