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
