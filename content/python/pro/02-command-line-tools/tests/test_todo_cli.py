import json
import subprocess
import sys
from pathlib import Path

import pytest

from todo_cli import main

HERE = Path(__file__).parent


def run(tmp_path, *args):
    return main(["--file", str(tmp_path / "todo.json"), *args])


def test_add_assigns_increasing_ids(tmp_path, capsys):
    assert run(tmp_path, "add", "write tests") == 0
    assert run(tmp_path, "add", "ship", "--priority", "3") == 0
    assert capsys.readouterr().out == "added 1\nadded 2\n"
    stored = json.loads((tmp_path / "todo.json").read_text())
    assert stored[1] == {"id": 2, "title": "ship", "priority": 3, "done": False}


def test_list_sorted_by_priority(tmp_path, capsys):
    run(tmp_path, "add", "low", "--priority", "1")
    run(tmp_path, "add", "mid")
    run(tmp_path, "add", "high", "--priority", "3")
    capsys.readouterr()
    assert run(tmp_path, "list") == 0
    assert capsys.readouterr().out == "[ ] 3 (p3) high\n[ ] 2 (p2) mid\n[ ] 1 (p1) low\n"


def test_done_hides_task_from_list(tmp_path, capsys):
    run(tmp_path, "add", "a")
    run(tmp_path, "add", "b")
    assert run(tmp_path, "done", "1") == 0
    assert capsys.readouterr().out.endswith("done 1\n")
    run(tmp_path, "list")
    assert capsys.readouterr().out == "[ ] 2 (p2) b\n"


def test_list_all_includes_done(tmp_path, capsys):
    run(tmp_path, "add", "a")
    run(tmp_path, "add", "b")
    run(tmp_path, "done", "1")
    capsys.readouterr()
    run(tmp_path, "list", "--all")
    assert capsys.readouterr().out == "[x] 1 (p2) a\n[ ] 2 (p2) b\n"


def test_done_unknown_id_goes_to_stderr(tmp_path, capsys):
    assert run(tmp_path, "done", "42") == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == "error: no task 42"


def test_bad_arguments_exit_2(tmp_path):
    with pytest.raises(SystemExit) as info:
        run(tmp_path, "add", "x", "--priority", "5")
    assert info.value.code == 2
    with pytest.raises(SystemExit) as info:
        run(tmp_path)
    assert info.value.code == 2


def test_runs_as_a_script(tmp_path):
    db = tmp_path / "t.json"
    script = HERE / "todo_cli.py"
    add = subprocess.run([sys.executable, script, "--file", db, "add", "from shell"], capture_output=True, text=True)
    assert add.returncode == 0 and add.stdout == "added 1\n"
    bad = subprocess.run([sys.executable, script, "--file", db, "done", "9"], capture_output=True, text=True)
    assert bad.returncode == 1 and "no task 9" in bad.stderr
