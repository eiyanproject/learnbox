---
title: Files and data
summary: Read and write text files safely using with, work with paths through pathlib, and handle CSV and JSON.
order: 11
files: [files.py]
run: python -i files.py
hints:
  - "`count_lines`: `with open(path) as f: return sum(1 for line in f if line.strip())`."
  - "`write_report(path, scores)`: open with `\"w\"` and write one `f\"{name}: {score}\\n\"` per item. `sorted(scores.items())` gives them in name order."
  - "`average_score(csv_path)`: use `csv.DictReader`; each row is a dict, so `float(row[\"score\"])`."
  - "`update_settings`: `json.loads(path.read_text())` if the file exists, else `{}`; `settings.update(changes)`; then `path.write_text(json.dumps(settings, indent=2))`."
---

Everything a program holds in variables disappears when it ends. Files are
how a program keeps data between runs, and how it reads data that something
else produced: a log, a spreadsheet export, a settings file. This lesson
covers plain text files and two common formats for structured data, CSV and
JSON.

## Opening a file

```python
with open("notes.txt") as f:
    text = f.read()
```

(This reads a file called `notes.txt`, which must already exist; the next
sections show what comes out.)

`open()` takes a path and gives back a **file object**, here named `f`: a
handle you read from or write to. A path without a folder in front, like
`"notes.txt"`, is looked up in the **current directory**, the folder the
program was started from. In this course that is your lesson folder, the one
the terminal opens in.

An open file uses resources from the operating system, and it should be
**closed** when you are done with it; data you wrote may not even reach the
disk until it is. `with` takes care of that: the file stays open for the
indented block and is closed automatically when the block ends, even if an
exception happens in the middle. Always open files this way.

The second argument is the **mode**, which says what you intend to do with
the file:

| Mode | Meaning |
|---|---|
| `"r"` | read (the default) |
| `"w"` | write: creates the file, or **empties** an existing one |
| `"a"` | append: add to the end, keeping what is there (creates the file if needed) |

Be careful with `"w"`: the moment the file is opened, anything it held is
gone, before you have written a single character.

Opening a file that does not exist in `"r"` mode raises `FileNotFoundError`.

## Reading

Suppose `notes.txt` holds these two lines:

```text
buy milk
call Ana
```

```python
with open("notes.txt") as f:
    whole = f.read()          # one string
print(repr(whole))

with open("notes.txt") as f:
    for line in f:            # one line at a time, memory friendly
        print(line.rstrip("\n"))
```

That prints:

```text
'buy milk\ncall Ana\n'
buy milk
call Ana
```

(`repr()` shows a string the way you would type it in code, quotes and all,
which makes the invisible line breaks visible as `\n`.)

There are two common ways to read. `f.read()` gives you the whole file as
one string. Looping over the file object with `for` gives you one line at a
time, which works however big the file is, because only one line is in
memory at once.

`\n` is how a line break is written inside a string: one character meaning
"new line". Each line you get from the loop keeps its `\n` at the end, the
line break that separated it from the next line. `print()` adds a line break
of its own, so printing the lines unchanged would show a blank line between
each pair. `.rstrip("\n")` removes the line break from the right-hand end;
`.strip()` removes it along with any other spaces at either end.

## Writing

```python
with open("out.txt", "w") as f:
    f.write("first line\n")    # write does not add a newline for you
    print("second line", file=f)

with open("out.txt") as f:     # read it back to see what was written
    print(f.read(), end="")
```

```output
first line
second line
```

`f.write()` writes exactly the string you give it and nothing more, so you
add the `\n` yourself; without it, the next write would carry on along the
same line. `write` also only accepts strings, so convert numbers with `str()`
or an f-string first. The other way is `print(..., file=f)`, which writes to
the file instead of the terminal and adds the line break for you, the same
as it does on screen. (`end=""` in the last `print` stops it adding a second
line break after the file's own.)

The file had to be closed, by the end of the first `with`, before reading it
back: until then, what you wrote may still be waiting in memory.

## Using code from elsewhere

The rest of this lesson uses tools that are not built in. Python ships with a
large collection of them, and you ask for one by name before you use it:

```python
import csv                        # now csv.reader, csv.writer exist
from pathlib import Path          # now Path exists, on its own
```

(This block only shows the two forms of `import`; it produces no output.)

A **module** is a file of Python code that somebody else already wrote. `import csv`
makes the whole module available as `csv.something`; `from pathlib import Path`
takes one name out of it and gives you that name directly. Either is fine - the
second saves typing when you only want one thing.

Put imports at the top of your file. You do not need to install any of the ones
below: they come with Python.

There is more to this - your own modules, packages, and other people's
libraries - in the Intermediate section.

## pathlib

A path is text, like `"data/scores.csv"`, but building and taking apart
paths with string operations is fiddly and error-prone. A `Path`
object understands the structure of a path: which part is the folder, which
is the file name, which is the extension. It is the modern way to handle file
paths:

```pycon
>>> from pathlib import Path
>>> p = Path("data") / "scores.csv"   # / joins path parts
>>> p.name
'scores.csv'
>>> p.suffix
'.csv'
>>> p.stem
'scores'
>>> p.parent
PosixPath('data')
```

The `/` here is not division: between `Path` objects (or a `Path` and a
string) it means "and then inside that, this", and puts the right separator
between the parts for you. `.name` is the last part, `.suffix` the extension,
`.stem` the name without the extension and `.parent` the folder it is in.
(`PosixPath` is how a path prints on Linux and macOS.)

Creating a `Path` does not touch the disk; it is only a description of a
location, and the file does not need to exist. These are the things you do
with the file it points at:

```pycon
>>> p.exists()                     # there is no data/scores.csv here
False
>>> note = Path("demo_note.txt")
>>> note.write_text("hello\n")     # replaces the file's contents, like "w"
6
>>> note.exists()
True
>>> note.read_text()               # whole file, opened and closed for you
'hello\n'
>>> note.unlink()                  # delete the file again
>>> note.exists()
False
```

`read_text()` and `write_text()` open, read or write, and close the file in
one step, so they need no `with`. They are the quickest way to deal with a
whole small file. `write_text` returns the number of characters it wrote,
which is the `6` the prompt shows (five letters and the `\n`); you can ignore
it. `unlink()` deletes a file (the name comes from the Unix term for it).

To go through everything in a folder, use `iterdir()`. `Path(".")` is the
current directory (`.` always means "here"):

```python
for child in Path(".").iterdir():
    print(child)
```

This prints one line per file and folder, so what you see depends on what is
in your folder. In this lesson's folder you would see `files.py` among them.

Functions that take a path, including `open()`, accept either a string or a
`Path`.

## CSV

CSV (comma-separated values) is the plain-text format spreadsheets export:
one row per line, with commas between the columns. The first line usually
holds the column names. A file like this:

```text
name,score
ana,9
bo,7
```

You could split each line on commas yourself, but the `csv` module also
copes with the awkward cases, such as a value that itself contains a comma
(which CSV puts in quotes). Read it like this:

```python
import csv

with open("scores.csv", newline="") as f:
    for row in csv.DictReader(f):
        print(row["name"], row["score"])   # every value is a string
```

`csv.DictReader` reads the first line as the column names, then gives you
each following row as a dict from column name to value. With the file above,
this prints `ana 9` and then `bo 7`.

`DictReader` accepts anything that hands out lines, not only an open file,
so you can try it at the prompt with a list of strings standing in for the
file:

```pycon
>>> import csv
>>> rows = list(csv.DictReader(["name,score", "ana,9", "bo,7"]))
>>> rows[0]
{'name': 'ana', 'score': '9'}
>>> rows[0]["score"] + rows[1]["score"]       # strings: joined, not added
'97'
>>> int(rows[0]["score"]) + int(rows[1]["score"])
16
```

Every value is a **string**, even if it looks like a number, because a CSV
file is only text. As the last two lines show, `+` on two strings joins them,
so convert with `int()` or `float()` before doing arithmetic. `newline=""` is
what the `csv` module asks for when opening the file: it lets the module
handle line endings itself.

## JSON

JSON (JavaScript Object Notation) is a text format for structured data, used
by web APIs and settings files everywhere. It looks almost like Python: JSON
objects are written like dicts, JSON arrays like lists, and its strings,
numbers, `true`, `false` and `null` correspond to Python's `str`, `int` and
`float`, `True`, `False` and `None`. So it maps neatly onto dicts and lists:

```pycon
>>> import json
>>> settings = {"theme": "dark", "size": 14}
>>> text = json.dumps(settings, indent=2)   # dict -> str
>>> print(text)
{
  "theme": "dark",
  "size": 14
}
>>> json.loads(text)                        # str -> dict
{'theme': 'dark', 'size': 14}
```

`json.dumps` (dump to a **s**tring) turns Python data into JSON text, and
`indent=2` lays it out over several lines, two spaces per level, so people
can read it. `json.loads` (load from a **s**tring) turns JSON text back into
Python data. Notice that JSON always writes strings with double quotes, while
Python shows them with single quotes; it is the same data either way.

`json.dump(obj, f)` and `json.load(f)`, without the `s`, do the same with an
open file instead of a string. With pathlib, `json.loads(p.read_text())` and
`p.write_text(json.dumps(data))` do the same job equally well.

Not every Python value has a JSON form. Dicts, lists, strings, numbers,
booleans and `None` do; a set, for example, does not, and `json.dumps` raises
`TypeError` for it. JSON object keys are always strings.

## Try it

Your workspace is a real directory, so files you create in the terminal and
files you create from Python are the same files. In the terminal, run
`echo "hello" > note.txt` (`echo` prints text, and `>` sends it into a file
instead of the screen). Then start `python` and type `open("note.txt").read()`
at the `>>>` prompt. You should see `'hello\n'`: the text plus the line break
that `echo` added. (At the prompt, skipping `with` for a quick look is fine;
in a program, use it.)

## Your turn

In `files.py`, each function receives a path (a `str` or a `Path`):

- `count_lines(path)`: the number of lines that are not blank. A line holding
  only spaces counts as blank. (`line.strip()` of a blank line is the empty
  string, which is falsy.)
- `write_report(path, scores)`: `scores` is a dict of name to number. Write
  one line per name, sorted by name, as `name: score`, each line ending with
  a line break. For `{"bo": 7, "ana": 9}` the file reads:

  ```text
  ana: 9
  bo: 7
  ```

- `average_score(csv_path)`: the file's first line is the header
  `name,score`, and every line after it is one row such as `ana,9`. Return
  the average of the scores as a float rounded to 1 decimal, or `0.0` if
  there are no rows (dividing by a count of zero would raise an error).
  Rows scoring 9, 8 and 8 average to `8.3`: 25 divided by 3 is 8.333...
- `update_settings(path, changes)`: the file holds a JSON object, and
  `changes` is a dict. Read the object (or start from `{}` if the file does
  not exist), copy every key of `changes` into it, replacing values already
  there, write the result back as JSON, and return it. If the file holds
  `{"theme": "dark", "size": 12}` and `changes` is
  `{"size": 14, "lang": "en"}`, the result is
  `{"theme": "dark", "size": 14, "lang": "en"}`.
