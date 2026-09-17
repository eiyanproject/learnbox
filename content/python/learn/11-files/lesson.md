---
title: Files and data
summary: Read and write text files safely with with, walk paths with pathlib, and handle CSV and JSON.
order: 11
files: [files.py]
run: python -i files.py
hints:
  - "`count_lines`: `with open(path) as f: return sum(1 for line in f if line.strip())`."
  - "`write_report(path, scores)`: open with `\"w\"` and write one `f\"{name}: {score}\\n\"` per item. `sorted(scores.items())` gives them in name order."
  - "`average_score(csv_path)`: use `csv.DictReader`; each row is a dict, so `float(row[\"score\"])`."
  - "`update_settings`: `json.loads(path.read_text())` if the file exists, else `{}`; `settings.update(changes)`; then `path.write_text(json.dumps(settings, indent=2))`."
---

## Opening a file

```python
with open("notes.txt") as f:
    text = f.read()
```

`with` closes the file when the block ends, even if an exception happens in
the middle. Always open files this way.

The second argument is the **mode**:

| Mode | Meaning |
|---|---|
| `"r"` | read (the default) |
| `"w"` | write: creates the file, or **empties** an existing one |
| `"a"` | append to the end |

## Reading

```python
with open("notes.txt") as f:
    whole = f.read()          # one string

with open("notes.txt") as f:
    for line in f:            # one line at a time, memory friendly
        print(line.rstrip("\n"))
```

Each line keeps its `\n` at the end; `.rstrip("\n")` or `.strip()` removes it.

## Writing

```python
with open("out.txt", "w") as f:
    f.write("first line\n")    # write does not add a newline for you
    print("second line", file=f)
```

## pathlib

`Path` objects are the modern way to handle file paths:

```python
from pathlib import Path

p = Path("data") / "scores.csv"   # / joins path parts
p.exists()
p.name        # 'scores.csv'
p.suffix      # '.csv'
p.read_text()                 # whole file, opened and closed for you
p.write_text("hello\n")
for child in Path(".").iterdir():
    print(child)
```

## CSV

```python
import csv

with open("scores.csv", newline="") as f:
    for row in csv.DictReader(f):
        print(row["name"], row["score"])   # every value is a string
```

The first line of the file is used as the column names.

## JSON

JSON maps neatly onto dicts and lists:

```python
import json

settings = {"theme": "dark", "size": 14}
text = json.dumps(settings, indent=2)   # dict -> str
back = json.loads(text)                 # str -> dict
```

`json.dump(obj, f)` and `json.load(f)` do the same with an open file.

## Try it

Your workspace is a real directory. In the terminal: `echo "hello" > note.txt`,
then at the `>>>` prompt `open("note.txt").read()`.

## Your turn

In `files.py`, each function receives a path (a `str` or a `Path`):

- `count_lines(path)`: the number of lines that are not blank
- `write_report(path, scores)`: `scores` is a dict of name to number. Write
  one line per name, sorted by name, as `name: score`.
- `average_score(csv_path)`: the file has a header `name,score`. Return the
  average score as a float rounded to 1 decimal, or `0.0` if there are no rows.
- `update_settings(path, changes)`: read a JSON object from the file (or start
  from `{}` if the file does not exist), apply `changes` over it, write it back
  as JSON, and return the updated dict
