---
title: "Capstone: a persistent key-value store"
summary: An append-only log with crash recovery, compaction with atomic replace, thread safety, a context manager API and a CLI.
order: 10
files: [kvstore.py]
run: python kvstore.py demo.db keys
hints:
  - "Opening: create the file if missing (`open(path, \"a\").close()`), then replay it line by line with `json.loads`. Apply `set` and `del` entries to a dict. A line that fails to parse can only be the last one (a crash mid-write): stop there."
  - "Writing: `json.dumps(entry) + \"\\n\"`, `self._file.write(...)`, `self._file.flush()`, all inside `with self._lock:` together with the dict update, so the log and memory never disagree."
  - "`compact()`: write one `set` line per current key to `path + \".tmp\"`, `flush` and `os.fsync`, close the append handle, `os.replace(tmp, path)`, then reopen for appending. `os.replace` is atomic."
  - "`main(argv)`: `db, command, *args = argv`; `with KVStore(db) as store:` then dispatch. Values given on the command line are stored as strings; `get` of a missing key prints to stderr and returns 1."
---

Time to combine the course into one small, real system: a database that
stores keys and values in a file, survives the program being killed at the
worst possible moment, can be used safely from several threads, and comes
with a command-line tool. It touches files and JSON (Beginner), context
managers and the data model (Intermediate and Advanced), threads and locks
(Advanced), and the CLI patterns from earlier in this section.

Databases like Bitcask, and the write-ahead logs inside PostgreSQL and
SQLite, rest on the same idea: **never modify data in place; append a record
of every change**. Rewriting a file in place is dangerous, because a crash
halfway through leaves it half old and half new. Adding to the end of a file
is much safer: a crash can only damage the part being added.

## The log

The file is a **log**: one JSON object per line, each describing one
change, in the order the changes happened:

```json
{"op": "set", "key": "name", "value": "Ana"}
{"op": "set", "key": "age", "value": 31}
{"op": "del", "key": "name"}
```

Reading it from the top: `name` was set to `"Ana"`, then `age` to `31`, then
`name` was deleted. So the current contents are `{"age": 31}`.

- **Writes** append a line: fast, and a crash can only damage the last line.
- **Opening** replays every line into an in-memory dict: start from `{}`,
  apply each `set` and `del` in order. After replay, reads are dict lookups,
  as fast as any dict.
- The in-memory state is always "the result of applying the log". If you
  ever doubt it, throw the dict away and replay the file: you get the same
  thing.

```pycon
>>> import json
>>> lines = [
...     '{"op": "set", "key": "name", "value": "Ana"}',
...     '{"op": "set", "key": "age", "value": 31}',
...     '{"op": "del", "key": "name"}',
... ]
>>> data = {}
>>> for line in lines:
...     entry = json.loads(line)
...     if entry["op"] == "set":
...         data[entry["key"]] = entry["value"]
...     elif entry["op"] == "del" and entry["key"] in data:
...         del data[entry["key"]]
...
>>> data
{'age': 31}
```

Values can be anything JSON can hold (strings, numbers, lists, dicts,
`True`, `None`), so the store can keep structured data, not only text.

## Crash recovery

If the process dies halfway through writing, the last line is truncated
JSON, cut off part way, and `json.loads` cannot parse it. Everything before
it is intact, because those lines were complete before the crash began. So
on replay: apply lines until one fails to parse, then stop.

```pycon
>>> torn = '{"op": "set", "key": "half", "va'
>>> json.loads(torn)
Traceback (most recent call last):
  ...
json.decoder.JSONDecodeError: Unterminated string starting at: line 1 column 30 (char 29)
```

`JSONDecodeError` is a subclass of `ValueError`, so `except ValueError`
catches it. Losing the half-written final change is correct: it was never
**acknowledged**. The `set` call that was writing it had not returned yet, so
no caller was ever told it succeeded.

Two calls control when data really reaches the disk. `flush()` hands
Python's buffered data to the operating system. `os.fsync(f.fileno())` asks
the operating system to write its own buffers to the physical disk, which is
slower. Without `flush`, a write may sit inside your program; without
`fsync`, it may sit in the operating system for a few seconds, and be lost if
the whole machine loses power. Real databases fsync on commit; here,
flushing each write is enough, and compaction fsyncs.

## Compaction

A key set a million times leaves a million lines, though only the last one
matters. **Compaction** rewrites the log with only the current state: one
`set` line per live key. It must never leave a half-written database behind,
so:

1. write the new log to a temporary file in the same directory,
2. flush and fsync it, so it is completely on disk,
3. `os.replace(tmp, path)`, which atomically swaps it in: readers see either
   the old complete file or the new complete file, never a mix.

**Atomic** means it happens as one indivisible step: there is no moment
in between at which the file is half replaced. `os.replace` is a rename,
which the operating system performs atomically when both files are on the
same disk, which is why the temporary file goes in the same directory. If the
program crashes before step 3, the old log is untouched, and the temporary
file is only clutter. If it crashes after, the new log is complete.

```pycon
>>> import os, tempfile
>>> folder = tempfile.mkdtemp()
>>> path = os.path.join(folder, "db")
>>> with open(path, "w") as f:
...     _ = f.write("old\n")
...
>>> with open(path + ".tmp", "w") as f:
...     _ = f.write("new\n")
...     f.flush()
...     os.fsync(f.fileno())
...
>>> os.replace(path + ".tmp", path)
>>> open(path).read(), os.path.exists(path + ".tmp")
('new\n', False)
```

## Concurrency

If two threads call `set` at once, their lines could interleave in the file,
or one thread could update the dict while the other is writing, leaving the
dict and the log disagreeing. A `threading.Lock` around "append to the file,
then update the dict" makes each write one indivisible step, which keeps the
two in step when several threads write at once (the race conditions from the
Threads lesson).

## API design

The store should feel like a Python object, not a file format:

```python
with KVStore("app.db") as db:
    db.set("user:1", {"name": "Ana"})
    db.get("user:1")
    "user:1" in db
    len(db)
```

A context manager guarantees the file is closed when the block ends, even if
it raises. Supporting `in` (`__contains__`) and `len` (`__len__`) makes the
store feel like a mapping (the data model lesson), so callers can use it
with the syntax they already know. Keys such as `"user:1"` are a common
convention for grouping keys in a flat store: the prefix says what kind of
record it is.

## Your turn

In `kvstore.py`, implement `KVStore(path)`. The starter has the methods'
names; you also need to add `__len__`, `__contains__`, `__enter__` and
`__exit__`.

- Opening a store creates the file if it does not exist, and replays it.
- `set(key, value)`, `get(key, default=None)`, `delete(key)` (returns `True`
  if the key existed and `False` if not; deleting a missing key writes
  nothing to the log), `keys()` (a sorted list), `len(db)` and `key in db`.
- Persistence across reopening, via the append-only JSON-lines log. Each
  entry is exactly `{"op": "set", "key": ..., "value": ...}` or
  `{"op": "del", "key": ...}`, one per line; a test reads the file directly.
- Tolerate a corrupt **final** line on open: keep everything before it.
- `log_entries()`: the number of lines in the log file.
- `compact()`: rewrite the log atomically with one line per live key, via a
  temporary file that must not be left behind. Writes after compacting must
  keep working.
- Thread-safe writes: six threads writing 200 keys each must give 1200 keys,
  both in memory and in the file. `close()`, and use as a context manager.

And `main(argv)` for the command line, returning an exit code. `argv` is the
list of arguments, database path first:

- `DB set KEY VALUE` stores the value as a string and prints `OK`.
- `DB get KEY` prints the value or, if the key is missing, prints
  `not found: KEY` to stderr and returns `1`.
- `DB del KEY` prints `1` or `0`; `DB keys` prints one key per line, sorted.
- `DB compact` prints `compacted <before> -> <after>`, the log's line count
  before and after: after `set greeting`, `set a` and `del a`, compacting
  prints `compacted 3 -> 1`.

Press **Run** to list the keys in `demo.db`; in the terminal, try
`python kvstore.py demo.db set name Ana` and the other commands, then
`cat demo.db` to see the log itself.
