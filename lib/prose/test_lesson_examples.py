"""Runs the examples in a lesson's prose.

`learnbox verify` writes lesson_examples.json and copies this file beside a
copy of the lesson's reference solution, then runs pytest here. It is never
part of a learner's Check: a broken example is the lesson's fault, not theirs.

Two kinds of example, each opted into by its format in lesson.md:

- ```pycon transcripts (the Python-based tracks). They run as doctests and
  share one namespace in the order they appear, the way a reader follows the
  lesson - an example may use a name an earlier one defined, or import the
  lesson's own module.
- A complete program directly followed by an ```output block (any track). It
  is compiled the way the lesson checks compile, run, and its standard output
  compared with the block.

A failure names the line in lesson.md.
"""

import difflib
import doctest
import io
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

_HERE = pathlib.Path(__file__).parent
_FILE = _HERE / "lesson_examples.json"
_DATA = json.loads(_FILE.read_text(encoding="utf-8")) if _FILE.exists() else {}
_LANG = _DATA.get("lang", "")
_PYCON = _DATA.get("pycon") or []
_PROGRAMS = _DATA.get("programs") or []
_OCTAVE_PATH = _DATA.get("octave_path") or ""


def _ids(blocks):
    return [f"lesson.md line {b['line']}" for b in blocks]


# ---------------------------------------------------------------- transcripts

# One namespace for the whole lesson, kept between blocks. It is __main__, as
# at a real >>> prompt, so an exception class an example defines is reported
# by its bare name, the way the learner will see it.
_GLOBS = {"__name__": "__main__"}

# ELLIPSIS lets an example write `...` for output it does not care about, such
# as a memory address; NORMALIZE_WHITESPACE keeps line wrapping in the prose
# from mattering.
_FLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

if _PYCON:
    @pytest.mark.parametrize("block", _PYCON, ids=_ids(_PYCON))
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


# ---------------------------------------------------------------- programs

_DOTNET_ENV = {
    "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
    "DOTNET_NOLOGO": "1",
    "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
    "DOTNET_CLI_HOME": os.path.join(os.environ.get("HOME", "/tmp"), ".cache", "dotnet"),
    "NUGET_PACKAGES": os.path.join(os.environ.get("HOME", "/tmp"), ".cache", "nuget"),
}

_CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <AssemblyName>example</AssemblyName>
    <NoWarn>CS8600;CS8602;CS8603;CS8618;CS8625</NoWarn>
  </PropertyGroup>
</Project>
"""


def _java_file(source):
    # A public top-level type must live in a file of the same name.
    m = re.search(r"public\s+(?:(?:final|abstract|sealed)\s+)*(?:class|record|interface|enum)\s+(\w+)", source)
    return (m.group(1) if m else "Main") + ".java"


def _plan(lang, source, work):
    """Write the program into work and return the (build, run) commands."""
    if lang == "python":
        # Beside the solution, so `import lesson_module` works as it does for
        # the learner.
        script = _HERE / f"_example_{work.name}.py"
        script.write_text(source, encoding="utf-8")
        return None, [sys.executable, str(script)], _HERE
    if lang == "rust":
        (work / "main.rs").write_text(source, encoding="utf-8")
        return ["rustc", "--edition", "2024", "-o", "example", "main.rs"], ["./example"], work
    if lang == "c":
        (work / "main.c").write_text(source, encoding="utf-8")
        return ["gcc", "-std=c17", "-pthread", "-o", "example", "main.c", "-lm"], ["./example"], work
    if lang == "cpp":
        (work / "main.cpp").write_text(source, encoding="utf-8")
        return ["g++", "-std=c++20", "-pthread", "-o", "example", "main.cpp"], ["./example"], work
    if lang == "java":
        name = _java_file(source)
        (work / name).write_text(source, encoding="utf-8")
        # Single-file source launch: compile and run in one step, no classpath.
        return None, ["java", name], work
    if lang == "csharp":
        (work / "Program.cs").write_text(source, encoding="utf-8")
        (work / "example.csproj").write_text(_CSPROJ, encoding="utf-8")
        build = ["dotnet", "build", "-c", "Release", "--nologo", "-v", "q",
                 "/p:UseSharedCompilation=false"]
        return build, ["dotnet", "bin/Release/net8.0/example.dll"], work
    if lang == "matlab":
        # Octave is the engine, as for the lesson checks, with lib/octave on
        # the path for the types it lacks. A script name must be an identifier.
        script = f"example_{work.name}.m"
        (work / script).write_text(source, encoding="utf-8")
        path = ["--path", _OCTAVE_PATH] if _OCTAVE_PATH else []
        return None, ["octave", "--no-gui", "--quiet", "--norc", *path, script], work
    pytest.fail(f"no way to run a {lang} program", pytrace=False)


def _normalise(text, loose):
    lines = [line.rstrip() for line in text.replace("\r", "").split("\n")]
    if loose:
        # Octave and MATLAB lay out displayed values differently, so for
        # MATLAB compare the words and ignore spacing and blank lines.
        lines = [" ".join(line.split()) for line in lines if line.strip()]
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    return "\n".join(lines) + "\n"


def _run(cmd, cwd, env):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=180)


if _PROGRAMS:
    @pytest.mark.parametrize("prog", _PROGRAMS, ids=_ids(_PROGRAMS))
    def test_lesson_program(prog):
        lang = "python" if _LANG in ("python", "ccna", "mindset", "security") else _LANG
        work = _HERE / "_examples" / str(prog["line"])
        work.mkdir(parents=True, exist_ok=True)
        build, run, cwd = _plan(lang, prog["source"], work)
        env = dict(os.environ, **(_DOTNET_ENV if lang == "csharp" else {}))
        where = f"lesson.md line {prog['line']}"

        if build:
            b = _run(build, cwd, env)
            if b.returncode != 0:
                pytest.fail(f"the program at {where} does not compile:\n{b.stdout}{b.stderr}", pytrace=False)
        r = _run(run, cwd, env)
        if r.returncode != 0:
            pytest.fail(f"the program at {where} exits with {r.returncode}:\n{r.stdout}{r.stderr}", pytrace=False)

        loose = lang == "matlab"
        want, got = _normalise(prog["output"], loose), _normalise(r.stdout, loose)
        if not doctest.OutputChecker().check_output(want, got, doctest.ELLIPSIS):
            diff = "".join(difflib.unified_diff(
                want.splitlines(True), got.splitlines(True), "the lesson says", "the program prints"))
            pytest.fail(f"the program at {where} does not print what the lesson shows:\n{diff}", pytrace=False)
