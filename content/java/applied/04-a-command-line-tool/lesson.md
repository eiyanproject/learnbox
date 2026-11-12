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
work, and tests that do not need a terminal. The program is a small text
tool, run like this:

```text
$ java Tool count --file notes.txt
3
$ java Tool find --file notes.txt --pattern cat
the cat sat
$ java Tool find --fil notes.txt
Unknown option: --fil
Usage: tool <count|words|find> --file <path> [--pattern <text>] [--verbose]
```

(Type each command without the `$`.) The first word after `Tool` is the
**command**, what to do; the words starting `--` are **options**, which
adjust how; and some options take a **value**, the word that follows them.

## Separate parsing from doing

```java
record Options(String command, String file, String pattern, boolean verbose) {}

Options parse(String[] args)                    // strings in, structure out
String run(Options options, List<String> lines) // structure in, result out
void main(String[] args)                        // the only part that does I/O
```

(Signatures only.) Three pieces, each testable alone:

- `parse` turns the raw words into an `Options` record, and rejects nonsense.
  It does not read the file or print anything.
- `run` does the actual work on lines it is *given*. It never reads a file,
  never prints, and never calls `System.exit`.
- `main` is the thin layer that glues them to the real world: it calls
  `parse`, reads the file named in the options, calls `run`, prints the
  result, and on an error prints a message and exits.

The middle one — the part with all the logic — is what makes it possible to
test the behaviour in milliseconds, by passing a `List.of("...")` of lines,
instead of writing fixture files to disk and capturing the console.

A `main` that does everything is the default shape of a first program and the
reason it cannot be tested at all. It is the same separation as the service
and its store in the previous lessons, with the console and the file system
as the parts kept at the edge.

## Arguments

`String[] args` holds what came after the class name, already split into
words by the shell: `java Tool count --file notes.txt` gives
`{"count", "--file", "notes.txt"}`. There is no program name at index 0 —
unlike C, unlike Python's `sys.argv`.

Parse it into something meaningful immediately. Passing a raw `String[]` deeper
into the program means every layer has to know the argument format.

Parsing is a walk along the array with an index:

1. Look at `args[i]`.
2. If it is an option that takes a value (`--file`, `--pattern`), the value is
   `args[i + 1]`; check that there *is* one, then move on two places.
3. If it is a flag with no value (`--verbose`), set it and move on one place.
4. If it starts with `--` but is none of those, it is unknown: reject it,
   naming it.
5. Otherwise it is a plain word: the command. Move on one place.

At the end, if no command was seen, reject that too.

## Failing usefully

```text
Unknown option: --fil
Usage: tool <count|words|find> --file <path> [--pattern <text>] [--verbose]
```

Three things a good error does: say what was wrong, say what was expected, and
exit non-zero so a script can tell. A stack trace does none of them — it is a
report for the author, not the user. So `main` catches the
`IllegalArgumentException` from `parse` or `run`, prints its message and the
usage line, and exits with a non-zero code, rather than letting the
exception crash out.

In the usage line, `<count|words|find>` means "one of these", `<path>` means
"a value you supply", and square brackets mean "optional".

By convention: exit 0 for success, non-zero for failure; results on stdout,
diagnostics on stderr (`System.err.println`), so
`tool find ... > results.txt` captures what you meant and still shows you the
errors. `System.exit(2)` ends the program with exit code 2, a common choice
for "you used the command wrongly".

## Your turn

In `Tool.java`:

- `record Options(String command, String file, String pattern, boolean verbose)`,
  declared inside the `Tool` class (the tests write `Tool.Options`)
- `static Options parse(String[] args)` — the first bare word is the command,
  `--file` and `--pattern` each take the next word as their value, and
  `--verbose` is a flag; options may come in any order, before or after the
  command. Throw `IllegalArgumentException` for an unknown option (with a
  message that contains the option, such as `"Unknown option: --fil"`), for
  `--file` or `--pattern` with no value after it, and when there is no
  command at all. Options not given are `null`, and `verbose` is `false`.
- `static String run(Options options, List<String> lines)` — `count` gives the
  number of lines, `words` the number of words (split on whitespace), both as
  strings such as `"3"`; `find` gives the lines containing the pattern,
  joined by newlines. `find` without a `--pattern` throws
  `IllegalArgumentException`, and so does an unknown command (`run` checks
  the command, not `parse`). An empty list of lines counts `"0"`.
- `static String usage()` — the usage line, naming all three commands
- a `main` that puts them together: parse, read the file with
  `Files.readAllLines`, run, and print; on an `IllegalArgumentException`,
  print the message and the usage to stderr and exit with status 2
