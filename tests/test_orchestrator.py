import orchestrator


def _build(folder, empty=()):
    folder.mkdir(parents=True)
    for name in orchestrator.GAME_FILES:
        (folder / name).write_text("" if name in empty else "x", encoding="utf-8")


def test_is_built_requires_all_files_non_empty(tmp_path):
    _build(tmp_path / "ok")
    assert orchestrator.is_built(tmp_path / "ok")


def test_is_built_false_when_file_empty(tmp_path):
    _build(tmp_path / "bad", empty=("game.js",))
    assert not orchestrator.is_built(tmp_path / "bad")


def test_is_built_false_when_folder_missing(tmp_path):
    assert not orchestrator.is_built(tmp_path / "nope")


def test_read_title(tmp_path):
    page = tmp_path / "game.html"
    page.write_text("<html><title> Quiz Time </title></html>", encoding="utf-8")
    assert orchestrator._read_title(page) == "Quiz Time"
    assert orchestrator._read_title(tmp_path / "missing.html") == ""


def test_team_status_and_finished_games(tmp_path):
    workers = [
        {"key": "a", "slug": "a", "name": "Alpha"},
        {"key": "b", "slug": "b", "name": "Beta"},
    ]
    team = orchestrator.Team("RAG", workers, tmp_path, tmp_path / "board.sqlite")
    _build(tmp_path / "a")
    (tmp_path / "a" / "game.html").write_text("<title>Alpha Game</title>", encoding="utf-8")

    status = team.status()
    assert "Alpha" in status and "built" in status and "NOT built" in status
    assert team.finished_games() == [{"label": "Alpha Game", "slug": "a"}]