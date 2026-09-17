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

Time to combine the track into one small, real system. Databases like Bitcask
and the write-ahead logs inside PostgreSQL and SQLite rest on the same idea:
**never modify data in place; append a record of every change**.

## The log

The file is one JSON object per line:

```json
{"op": "set", "key": "name", "value": "Ana"}
{"op": "set", "key": "age", "value": 31}
{"op": "del", "key": "name"}
```

- **Writes** append a line: fast, and a crash can only damage the last line.
- **Opening** replays every line into an in-memory dict. After replay, reads
  are dict lookups.
- The in-memory state is always "the result of applying the log".

## Crash recovery

If the process dies halfway through writing, the last line is truncated JSON.
Everything before it is intact. So on replay: apply lines until one fails to
parse, then stop. Losing the half-written final change is correct: it was never
acknowledged.

`flush()` hands data to the operating system; `os.fsync()` asks it to reach the
disk. Real databases fsync on commit; here, flushing each write is enough.

## Compaction

A key set a million times leaves a million lines. **Compaction** rewrites the
log with just the current state. It must never leave a half-written database
behind, so:

1. write the new log to a temporary file in the same directory,
2. flush and fsync it,
3. `os.replace(tmp, path)`, which atomically swaps it in: readers see either the
   old complete file or the new complete file, never a mix.

## Concurrency

A `threading.Lock` around "append to the file, then update the dict" keeps the
two in step when several threads write at once.

## API design

```python
with KVStore("app.db") as db:
    db.set("user:1", {"name": "Ana"})
    db.get("user:1")
    "user:1" in db
    len(db)
```

A context manager guarantees the file is closed. Supporting `in` and `len`
makes the store feel like a mapping (the data model lesson).

## Your turn

In `kvstore.py`, implement `KVStore(path)`:

- `set(key, value)`, `get(key, default=None)`, `delete(key)` (returns whether
  the key existed; deleting a missing key writes nothing), `keys()` (sorted),
  `__len__`, `__contains__`
- persistence across reopening, via the append-only JSON-lines log
- tolerate a corrupt **final** line on open
- `log_entries()`: number of lines in the log file
- `compact()`: rewrite the log atomically with one line per live key
- thread-safe writes; `close()`, and use as a context manager

And `main(argv)` for the command line, returning an exit code:

- `DB set KEY VALUE` prints `OK`; `DB get KEY` prints the value or, if missing,
  prints `not found: KEY` to stderr and returns `1`
- `DB del KEY` prints `1` or `0`; `DB keys` prints one key per line;
  `DB compact` prints `compacted <before> -> <after>`
