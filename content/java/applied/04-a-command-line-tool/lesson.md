---
title: "Capstone: a command line tool"
summary: Arguments, a parsed configuration, a core that does not touch the console, and errors that tell the user what to do.
order: 4
files: [Tool.java]
run: javac Tool.java && java Tool count --file notes.txt
hints:
  - "`parse(String[] args)` returns an Options record. Walk the array: the first non-flag word is the command, `--file X` sets the file, `--verbose` sets a boolean."
  - "Unknown flags should throw IllegalArgumentException with a message naming the flag - that is what makes a CLI usable."
  - "`run(Options, List<String> lines)` takes the lines rather than reading a file, so the logic is testable without touching the disk."
  - "`count` returns the number of lines, `words` the number of words, `find` the lines containing options.pattern()."
---

Everything so far ends here: types to model the input, a service that does the
work, and tests that do not need a terminal.

## Separate parsing from doing

```java
record Options(String command, String file, String pattern, boolean verbose) {}

Options parse(String[] args)                    // strings in, structure out
String run(Options options, List<String> lines) // structure in, result out
void main(String[] args)                        // the only part that does I/O
```

Three pieces, each testable alone. The middle one — the part with all the
logic — never reads a file, never prints, and never calls `System.exit`. That
is what makes it possible to test the behaviour in milliseconds instead of
writing fixture files.

A `main` that does everything is the default shape of a first program and the
reason it cannot be tested at all.

## Arguments

`String[] args` holds what came after the class name, already split by the
shell. No program name at index 0 — unlike C, unlike Python's `sys.argv`.

Parse it into something meaningful immediately. Passing a raw `String[]` deeper
into the program means every layer has to know the argument format.

## Failing usefully

```
Unknown option: --fil
Usage: tool <count|words|find> --file <path> [--pattern <text>] [--verbose]
```

Three things a good error does: say what was wrong, say what was expected, and
exit non-zero so a script can tell. A stack trace does none of them — it is a
report for the author, not the user.

By convention: exit 0 for success, non-zero for failure; results on stdout,
diagnostics on stderr, so `tool find ... > results.txt` captures what you meant
and still shows you the errors.

## Your turn

In `Tool.java`:

- `record Options(String command, String file, String pattern, boolean verbose)`
- `static Options parse(String[] args)` — the first bare word is the command,
  `--file`, `--pattern` take a value, `--verbose` is a flag, anything else
  throws `IllegalArgumentException`
- `static String run(Options options, List<String> lines)` — `count` gives the
  line count, `words` the word count, `find` the matching lines joined by
  newlines; an unknown command throws
- `static String usage()` — the usage line
