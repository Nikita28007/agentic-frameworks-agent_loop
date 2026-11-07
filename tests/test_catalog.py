from pathlib import Path

import catalog


def test_discover_finds_all_four_workers():
    found = catalog.discover()
    assert {w["key"] for w in found} == {"strands", "pydantic", "maf", "agno"}
    assert all(w["slug"] == w["key"] for w in found)


def test_discover_skips_requested_keys():
    found = catalog.discover(skip=("agno",))
    assert "agno" not in {w["key"] for w in found}
    assert len(found) == 3


def test_discover_ignores_missing_worker_files(tmp_path, monkeypatch):
    monkeypatch.setattr(catalog, "HERE", tmp_path)
    assert catalog.discover() == []


def test_launch_argv_runs_worker_without_sync():
    worker = catalog.WORKERS[0]
    argv = catalog.launch_argv(worker, 7, Path("/tmp/board.sqlite"))
    assert argv[1:3] == ["run", "--no-sync"]
    assert "--project" in argv
    assert argv[-2:] == ["7", str(Path("/tmp/board.sqlite"))]
    assert argv[-3].endswith("strands_worker.py")