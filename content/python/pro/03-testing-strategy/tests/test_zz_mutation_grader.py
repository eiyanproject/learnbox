"""Grades the learner's test_inventory.py by running it against mutants."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
MUTANTS = HERE / "mutants"
REFERENCE = MUTANTS / "reference.py"


def run_suite(tmp_path, implementation):
    work = tmp_path / implementation.stem
    work.mkdir()
    shutil.copy(implementation, work / "inventory.py")
    shutil.copy(HERE / "test_inventory.py", work / "test_inventory.py")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "test_inventory.py"],
        cwd=work,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result


def test_suite_passes_on_correct_code(tmp_path):
    result = run_suite(tmp_path, REFERENCE)
    assert result.returncode == 0, "your tests must pass against the real inventory.py:\n" + result.stdout[-1500:]


def test_suite_has_several_tests():
    source = (HERE / "test_inventory.py").read_text()
    assert source.count("def test_") >= 5, "write more than a handful of tests"


MUTANT_FILES = sorted(p for p in MUTANTS.glob("m*.py"))


@pytest.mark.parametrize("mutant", MUTANT_FILES, ids=lambda p: p.stem)
def test_mutant_is_caught(tmp_path, mutant):
    note = mutant.read_text().splitlines()[0].lstrip("# ")
    result = run_suite(tmp_path, mutant)
    assert result.returncode != 0, f"a mutant survived: {note}"
