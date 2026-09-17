import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def run():
    return subprocess.run(
        [sys.executable, str(HERE / "hello.py")],
        capture_output=True, text=True, timeout=10,
    )


def test_program_runs_without_errors():
    result = run()
    assert result.returncode == 0, result.stderr


def test_first_line_greets_learnbox():
    lines = run().stdout.splitlines()
    assert lines, "the program printed nothing"
    assert lines[0] == "Hello, learnbox!"


def test_second_line():
    lines = run().stdout.splitlines()
    assert len(lines) >= 2, "expected two lines of output"
    assert lines[1] == "Python is running."


def test_exactly_two_lines():
    assert len(run().stdout.splitlines()) == 2
