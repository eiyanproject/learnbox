"""Runs a lesson's >>> examples as doctests.

`learnbox verify` copies this file, and the lesson's ```pycon blocks as
lesson_examples.json, into its scratch workspace beside the reference solution.
It is never part of a learner's Check: a broken example is the lesson's fault,
not theirs.

The blocks share one namespace and run in the order they appear, the way a
reader follows the lesson - an example may use a name an earlier one defined,
or import the lesson's own module. A failure names the line in lesson.md.
"""

import doctest
import io
import json
import pathlib

import pytest

_FILE = pathlib.Path(__file__).with_name("lesson_examples.json")
_BLOCKS = json.loads(_FILE.read_text(encoding="utf-8")) if _FILE.exists() else []

# One namespace for the whole lesson, kept between blocks.
_GLOBS = {"__name__": "__lesson__"}

# ELLIPSIS lets an example write `...` for output it does not care about, such
# as a memory address; NORMALIZE_WHITESPACE keeps line wrapping in the prose
# from mattering.
_FLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


@pytest.mark.parametrize("block", _BLOCKS, ids=[f"lesson.md line {b['line']}" for b in _BLOCKS])
def test_lesson_example(block):
    test = doctest.DocTestParser().get_doctest(
        block["source"], _GLOBS, "lesson.md", "lesson.md",
        # get_doctest wants the 0-based line the text starts on.
        block["line"] - 1,
    )
    report = io.StringIO()
    runner = doctest.DocTestRunner(optionflags=_FLAGS)
    runner.run(test, out=report.write, clear_globs=False)
    # DocTest works on a copy of the namespace; hand the names back so the
    # next block sees what this one defined.
    _GLOBS.update(test.globs)
    if runner.failures:
        # pytrace=False: the reader needs the doctest report, not this harness.
        pytest.fail("lesson example does not do what the lesson says:\n" + report.getvalue(), pytrace=False)
