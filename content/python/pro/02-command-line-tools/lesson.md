---
title: Command-line tools
summary: Build a real CLI with argparse subcommands, testable main(argv), exit codes, stdin/stdout, and errors on stderr.
order: 2
files: [todo_cli.py]
run: python todo_cli.py --help
hints:
  - "Build the parser in its own function; `sub = parser.add_subparsers(dest=\"command\", required=True)` then `add = sub.add_parser(\"add\")`, `add.add_argument(\"title\")`, `add.add_argument(\"--priority\", type=int, choices=range(1, 4), default=2)`."
  - "`main(argv=None)`: `args = build_parser().parse_args(argv)`. argparse exits with status 2 on bad input by raising `SystemExit`, which the tests expect."
  - "Store tasks as JSON in `args.file`: read with `json.loads(path.read_text())` if it exists, else `[]`."
  - "`done` with an unknown id: `print(f\"error: no task {args.id}\", file=sys.stderr)` and `return 1`. `list` sorts by `(-priority, id)` and prints `[x] 1 (p3) title` style lines."
---

A command-line tool is a program whose interface is its arguments, standard
streams and exit code. Getting those right makes it scriptable, testable and
pleasant.

## argparse

```python
import argparse

def build_parser():
    p = argparse.ArgumentParser(prog="notes", description="Keep short notes.")
    p.add_argument("--file", default="notes.json", help="where notes are stored")
    sub = p.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a note")
    add.add_argument("text")
    add.add_argument("--tag", action="append", default=[])

    ls = sub.add_parser("list")
    ls.add_argument("--limit", type=int, default=10)
    return p
```

You get `--help`, type conversion, `choices`, and useful error messages for
free. `action="store_true"` makes flags; `nargs="+"` collects several values.

## A testable main

Put the logic in `main(argv=None)` and return an exit code:

```python
def main(argv=None):
    args = build_parser().parse_args(argv)     # None means sys.argv[1:]
    if args.command == "add":
        ...
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Tests can now call `main(["add", "buy milk"])` directly instead of spawning a
process.

## Exit codes and streams

- `0` means success; anything else is failure. argparse uses `2` for usage
  errors (it raises `SystemExit(2)`).
- **stdout** is for results (what a user might pipe into another program).
- **stderr** is for errors and diagnostics: `print("error: ...", file=sys.stderr)`.
- Read from stdin when it makes sense: `for line in sys.stdin:`.

Being strict about this is what makes `tool list | grep urgent` and
`if tool check; then ...` work.

## Packaging a CLI

In a real project, `pyproject.toml` turns `main` into an installed command:

```toml
[project.scripts]
todo = "todo_cli:main"
```

## Your turn

`todo_cli.py` is a to-do tool storing tasks in a JSON file (a list of
`{"id", "title", "priority", "done"}`). Implement `main(argv=None)` with a
global `--file` option (default `todo.json`) and subcommands:

- `add TITLE [--priority 1|2|3]` (default 2): ids start at 1 and increase;
  print `added <id>`
- `list [--all]`: undone tasks only unless `--all`, sorted by priority (high
  first) then id, one per line as `[ ] 2 (p3) write tests` (`[x]` when done)
- `done ID`: mark done and print `done <id>`; an unknown id prints
  `error: no task <id>` to **stderr** and returns `1`

Return `0` on success. Invalid arguments (such as priority 5) must exit with status `2`.
