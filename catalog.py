"""The worker manifest: which framework builds which game, how to launch it, and
the colour it flies on the live board.

"""

from __future__ import annotations

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent

# One record per framework, in the order they were taught. key is also the slug,
# the folder its game is built into; file is relative to this folder; colour is a
# rich colour for the live board; runner picks the launcher (python or node).
WORKERS = [
    {"key": "strands", "name": "AWS Strands", "colour": "cyan", "file": "workers/strands_worker.py", "runner": "python"},
    {"key": "pydantic", "name": "Pydantic AI", "colour": "green", "file": "workers/pydantic_worker.py", "runner": "python"},
    {"key": "maf", "name": "Microsoft Agent Framework", "colour": "magenta", "file": "workers/maf_worker.py", "runner": "python"},
    {"key": "agno", "name": "Agno", "colour": "yellow", "file": "workers/agno_worker.py", "runner": "python"},
    
    
]


def discover(skip: tuple[str, ...] = ()) -> list[dict]:
    """The workers whose files exist on disk, minus any skipped by key. Each result
    is its manifest record with slug set to its key (the folder its game builds into);
    the game itself is invented at runtime, so nothing about it is fixed here."""
    found = []
    for worker in WORKERS:
        if worker["key"] in skip:
            continue
        if (HERE / worker["file"]).exists():
            found.append({**worker, "slug": worker["key"]})
    return found


def launch_argv(worker: dict, task_id: int, board_path: Path) -> list[str]:
    """The subprocess argv that runs a worker against the shared board.

    uv is resolved to its full path with shutil.which, because on Windows subprocess.Popen
    does not consult PATHEXT for .cmd/.exe shims. --project pins the environment to this
    repo regardless of the worker's cwd; --no-sync avoids four parallel launches racing to
    sync the environment (the orchestrator itself was started with `uv run`, which already synced it)."""
    path = str((HERE / worker["file"]).resolve())
    return [shutil.which("uv") or "uv", "run", "--no-sync", "--project", str(HERE),
            path, str(task_id), str(board_path)]