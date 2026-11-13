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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **command-line tool** (CLI) | a program driven by the arguments typed after its name |
| **argument** | a word typed after the program name; `sys.argv` holds them as strings |
| **option** | an argument starting with `--`: optional, and named (`--file data.json`) |
| **positional argument** | an argument without dashes: required, identified by where it appears |
| **flag** | an on/off option, `False` unless given |
| **subcommand** | a word choosing an action with its own arguments, as in `git add` |
| **parser** | the object that turns the arguments into named values |
| **usage message** | the short summary of how to call a tool, shown on errors and with `--help` |
| **exit code** (exit status) | the number a process finishes with: `0` success, anything else failure; argparse uses `2` for usage errors |
| **standard streams** | a process's three channels: stdin, stdout, stderr |
| **stdout** (standard output) | for results; what `print()` writes and `\|` pipes on |
| **stderr** (standard error) | for errors and diagnostics, kept out of piped results |
| **stdin** (standard input) | where a program reads input from, such as a pipe |
| **pipe** (`\|`) | sends one program's stdout into another's stdin |
| **scriptable** | drivable by other programs and shell scripts |
| **`pyproject.toml`** | the standard project settings file |
| **entry point** | `todo = "todo_cli:main"`: an installed command that calls a function |
| **priority** | here 1 to 3, where 3 is the highest |

### Python names and functions

| Name | What it does |
|---|---|
| `argparse.ArgumentParser(prog=..., description=...)` | creates a parser; `prog` is the name shown in help |
| `p.add_argument("--file", default=..., help=...)` | declares an option |
| `p.add_argument("text")` | declares a positional argument |
| `type=int`, `choices=range(1, 4)` | convert to a number; allow only those values |
| `action="append"`, `action="store_true"`, `nargs="+"` | collect repeated values; an on/off flag; one or more values |
| `p.add_subparsers(dest="command", required=True)` | creates subcommands, storing the chosen one in `args.command` |
| `sub.add_parser("add")` | a subcommand with its own arguments |
| `p.parse_args(argv)` | the arguments as an object; `None` reads `sys.argv[1:]` |
| `def main(argv=None): ... return 0` | the testable entry point, returning an exit code |
| `sys.exit(main())` | ends the program with `main`'s exit code |
| `print(..., file=sys.stderr)` | writes to stderr |
| `for line in sys.stdin:` | reads input line by line |
| `json.loads`, `json.dumps`, `Path.read_text`, `Path.write_text` | read and save the task file |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python todo_cli.py --help` | shows the tool's help |
| `python todo_cli.py --file x.json list` | a global option before the subcommand |
| `echo "exit code: $?"` | `$?` holds the exit code of the last command |
| `tool list \| grep urgent` | pipes results into `grep`, which keeps matching lines |
| `if tool check; then ...` | the shell's `if` tests the exit code |

### Errors

| Error | Means |
|---|---|
| `SystemExit` | how argparse (and `sys.exit`) ends the program; status 2 for bad input |

---

A command-line tool is a program whose whole interface is three things: the
**arguments** typed after its name (`git commit -m "fix"`), the **standard
streams** it reads and writes (input from the keyboard or a pipe, output to
the screen or a file), and the **exit code** it finishes with. Getting those
three right is what makes a tool scriptable (other programs and shell
scripts can drive it), testable, and pleasant to use. This lesson builds one
properly.

## argparse

`sys.argv` holds the raw arguments as a list of strings, but parsing them by
hand (which ones are options, which take values, what is missing) gets messy
fast. The standard library's `argparse` module does it from a description of
what your tool accepts:

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

What each line declares:

- `ArgumentParser(prog=..., description=...)` creates the parser; `prog` is
  the name shown in help and errors.
- An argument name starting with `--` is an **option**: optional, and named
  on the command line (`--file data.json`). One without dashes, like
  `"text"`, is a **positional** argument: required, and identified by where
  it appears.
- `add_subparsers` creates **subcommands**, as in `git add` and
  `git commit`: each has its own arguments. `dest="command"` stores which one
  was used in `args.command`, and `required=True` makes choosing one
  mandatory.
- `type=int` converts the text to a number (and reports a clear error if it
  is not one). `action="append"` lets an option be given several times,
  collecting the values into a list.

`parse_args(list_of_strings)` turns arguments into an object with one
attribute per argument. Passing a list explicitly, instead of letting it read
the real command line, is also how you try it out:

```pycon
>>> import argparse
>>> def build_parser():
...     p = argparse.ArgumentParser(prog="notes", description="Keep short notes.")
...     p.add_argument("--file", default="notes.json", help="where notes are stored")
...     sub = p.add_subparsers(dest="command", required=True)
...     add = sub.add_parser("add", help="add a note")
...     add.add_argument("text")
...     add.add_argument("--tag", action="append", default=[])
...     ls = sub.add_parser("list")
...     ls.add_argument("--limit", type=int, default=10)
...     return p
...
>>> args = build_parser().parse_args(["add", "buy milk", "--tag", "home", "--tag", "today"])
>>> args.command, args.text, args.tag, args.file
('add', 'buy milk', ['home', 'today'], 'notes.json')
>>> build_parser().parse_args(["list", "--limit", "3"]).limit     # already an int
3
```

You get `--help`, type conversion, `choices` (only certain values allowed),
and useful error messages for free. Bad input makes argparse print a usage
message and an error to stderr, then exit with status 2, which it does by
raising `SystemExit`:

```pycon
>>> build_parser().parse_args(["list", "--limit", "many"])
Traceback (most recent call last):
  ...
SystemExit: 2
```

On screen, that also prints
`notes list: error: argument --limit: invalid int value: 'many'` (with a
usage line above it). Two more options you will use often: `action="store_true"`
makes an on/off flag, `False` unless it is given, and `nargs="+"` collects
one or more values into a list.

## A testable main

Put the logic in a `main(argv=None)` function and have it **return** an exit
code, rather than doing the work at the top level of the file:

```python
def main(argv=None):
    args = build_parser().parse_args(argv)     # None means sys.argv[1:]
    if args.command == "add":
        ...
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

`parse_args(None)` reads the real command line (`sys.argv[1:]`, everything
after the program name), so running the script works as normal.
`sys.exit(main())` passes the returned number to the operating system as the
exit code. Under the `__main__` guard (the Modules lesson), none of this runs
on import.

The payoff is testing. Tests can now call `main(["add", "buy milk"])` directly
with any arguments they like, and check the return value and the printed
output, instead of starting a separate process each time.

## Exit codes and streams

Every process finishes with a small number, its **exit code**, which the
shell and other programs can check:

- `0` means success; anything else is failure. Tools often use different
  numbers for different failures. argparse uses `2` for usage errors (it
  raises `SystemExit(2)`).

Every process also starts with three streams:

- **stdout** (standard output) is for results: what a user might **pipe**
  into another program with `|`. `print()` writes here.
- **stderr** (standard error) is for errors and diagnostics:
  `print("error: ...", file=sys.stderr)`. It still shows on the screen, but
  is kept separate, so error messages are not mixed into piped results.
- **stdin** (standard input) is where a program reads input from; read it
  when it makes sense, with `for line in sys.stdin:`, so your tool can sit in
  the middle of a pipeline.

Being strict about this is what makes `tool list | grep urgent` work (only
results go down the pipe; errors still reach the screen) and
`if tool check; then ...` work (the shell's `if` tests the exit code).

```console
$ python todo_cli.py done 9; echo "exit code: $?"
error: no task 9
exit code: 1
```

(`$?` in the shell holds the exit code of the last command.)

## Packaging a CLI

In a real project, an entry in `pyproject.toml` (the standard project
settings file) turns `main` into an installed command, so users can type
`todo` instead of `python todo_cli.py`:

```toml
[project.scripts]
todo = "todo_cli:main"
```

`"todo_cli:main"` means "the function `main` in the module `todo_cli`".
Installing the project creates a small `todo` program that imports it, calls
`main()`, and exits with whatever it returns.

## Your turn

`todo_cli.py` is a to-do tool storing tasks in a JSON file: a list of
objects like `{"id": 1, "title": "write tests", "priority": 2, "done": false}`.
Implement `main(argv=None)` with a global `--file` option (default
`todo.json`; it goes before the subcommand, as in
`todo_cli.py --file x.json list`) and these subcommands:

- `add TITLE [--priority 1|2|3]` (default 2): ids start at 1 and increase by
  one for each new task; save the task as not done, and print `added <id>`.
  Any other priority, such as 5, must make argparse exit with status 2.
- `list [--all]`: undone tasks only, unless `--all` is given; sorted by
  priority (3, the highest, first) and then by id; one per line as
  `[ ] 2 (p3) write tests`, that is, the box (`[x]` when done), the id, the
  priority as `p` plus its number in brackets, and the title.
- `done ID`: mark the task done and print `done <id>`. An unknown id prints
  `error: no task <id>` to **stderr**, prints nothing to stdout, and returns
  `1`.

Return `0` on success. Running with no subcommand at all must also exit with
status `2`. A file that does not exist yet means an empty list. A test also
runs the file as a real script, so keep the `sys.exit(main())` guard.
