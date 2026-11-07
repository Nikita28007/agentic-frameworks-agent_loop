import board


def test_reset_creates_empty_board(tmp_path):
    path = tmp_path / "board.sqlite"
    board.reset_board(path)
    assert board.list_todos(path) == []


def test_goal_and_steps_are_linked(tmp_path):
    path = tmp_path / "board.sqlite"
    board.reset_board(path)
    goal = board.add_goal("build game", path)
    s1 = board.add_step(goal, "write html", path)
    s2 = board.add_step(goal, "write js", path)

    todos = board.list_todos(path)
    assert [t["id"] for t in todos] == [goal, s1, s2]
    assert todos[0]["parent_id"] is None
    assert todos[1]["parent_id"] == goal and todos[2]["parent_id"] == goal
    assert all(t["status"] == "pending" for t in todos)


def test_claim_then_complete(tmp_path):
    path = tmp_path / "board.sqlite"
    board.reset_board(path)
    goal = board.add_goal("build game", path)

    board.claim_todo(goal, path)
    assert board.list_todos(path)[0]["status"] == "in_progress"

    board.complete_todo(goal, "done: 3 files", path)
    todo = board.list_todos(path)[0]
    assert todo["status"] == "done"
    assert todo["result"] == "done: 3 files"


def test_reset_drops_existing_todos(tmp_path):
    path = tmp_path / "board.sqlite"
    board.reset_board(path)
    board.add_goal("old goal", path)
    board.reset_board(path)
    assert board.list_todos(path) == []


def test_format_marks_status():
    done = {"id": 1, "task": "t", "status": "done", "result": "ok"}
    active = {"id": 2, "task": "t", "status": "in_progress", "result": ""}
    pending = {"id": 3, "task": "t", "status": "pending", "result": ""}
    assert "[strike]" in board._format(done, "Goal", "") and "ok" in board._format(done, "Goal", "")
    assert board._format(active, "Goal", "").startswith("[yellow]")
    assert board._format(pending, "Step", "  ") == "  Step #3: t"