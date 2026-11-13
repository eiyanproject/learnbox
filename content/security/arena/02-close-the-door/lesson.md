---
title: "Round 2: Close the door"
summary: A file server builds paths from what users type. Make it impossible to leave the folder.
order: 2
files: [files.py]
run: python -i files.py
challenge:
  minutes: 15
  xp: 200
  requires:
    xp: 900
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **file server** | a program that hands out files on request |
| **base folder** | the one folder whose files may be served, such as `/srv/files` |
| **requested path** | what the user typed to ask for a file |
| **path traversal** | using `..` to climb out of the base folder (Web lesson 5) |
| **tidy** (normalise) a path | remove `.`, `..` and doubled slashes: `a/../b.txt` becomes `b.txt` |
| **absolute path** | one starting with `/`, which ignores the base folder |
| **prefix trap** | `/srv/files-private` starts with the same letters as `/srv/files`, yet is outside it |
| **backslash** (`\`) | the Windows path separator; some systems treat it as `/`, so it can slip past a check |
| **NUL character** (`\x00`) | a zero byte; lower-level code may stop reading at it, cutting the path short |
| **`Forbidden`** | the exception in `files.py` to raise for a refused request |
| **POSIX paths** | paths with forward slashes, as on Linux |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -i files.py` | runs your file, then leaves Python open so you can try `resolve(...)` |

### Python names

| Name | What it does |
|---|---|
| `import posixpath` | path functions that always use `/`, on every machine |
| `posixpath.join(base, requested)` | joins the two with `/` (an absolute `requested` replaces `base`) |
| `posixpath.normpath(path)` | the tidied path |
| `requested.startswith("/")` | the request is absolute |
| `"\\" in requested`, `"\x00" in requested` | the request contains a backslash; a NUL |
| `full.startswith(base + "/")` | the tidied path is inside the base folder, not merely starting with the same letters |
| `raise Forbidden(...)` | refuses the request |

---

A small file server hands out documents from one folder. The review found
that `resolve` trusts whatever the user asks for, and the fix is due before
the next deploy.

## The task

In `files.py`, fix `resolve(base, requested)`.

`base` is the folder that may be served, such as `/srv/files`. `requested`
is what the user typed. Return the full, tidied path of the file, or raise
the `Forbidden` exception already defined in the file.

What must still work:

```text
resolve("/srv/files", "report.txt")          ->  "/srv/files/report.txt"
resolve("/srv/files", "2026/q1/notes.txt")   ->  "/srv/files/2026/q1/notes.txt"
resolve("/srv/files", "a/../b.txt")          ->  "/srv/files/b.txt"
resolve("/srv/files", "./a//b.txt")          ->  "/srv/files/a/b.txt"
```

What must raise `Forbidden`:

- anything that ends up **outside** `base` once the path is tidied, such as
  `../etc/passwd` or `a/../../secret`
- a path that only looks inside: with a base of `/srv/files`,
  `../files-private/x` tidies to `/srv/files-private/x`, which starts with
  the same letters and is a different folder
- an absolute path, such as `/etc/passwd`
- the folder itself: `.`, `a/..` or an empty string name no file
- a backslash or a NUL character (`"\x00"`) anywhere in the request: both
  are ways of smuggling a path past a check

Paths here always use forward slashes, so use `posixpath` rather than
`os.path`: `posixpath.join` and `posixpath.normpath` behave the same on
every machine. Decide on the tidied path, never on the text as typed.
