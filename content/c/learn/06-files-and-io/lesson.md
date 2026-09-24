---
title: Files, streams and checking every call
summary: FILE*, the three standard streams, and the return values that C programs are famous for ignoring.
order: 6
files: [io.c, io.h]
run: gcc -std=c17 -Wall io.c -o io && ./io
hints:
  - "`write_lines` opens with \"w\", writes each line followed by a newline, closes, and returns the number written - or -1 if fopen failed."
  - "`count_lines` counts newline characters with fgetc, which is the simplest correct way and handles a missing final newline sensibly."
  - "Always check fopen for NULL. The tests call these with a path that cannot be opened, and expect -1 rather than a crash."
  - "`read_first_line` must not overflow: fgets takes the buffer size and never writes more, unlike gets, which was removed from the language."
---

C's file API is built on `FILE *`, an opaque handle wrapping a buffered stream.

```c
FILE *f = fopen("notes.txt", "r");
if (f == NULL) { /* it failed, and errno says why */ }
...
fclose(f);
```

Modes: `"r"` read, `"w"` truncate-or-create, `"a"` append, and `"r+"`/`"w+"`
for read-write. Adding `"b"` matters on Windows and does nothing on Linux.

Three streams exist already: `stdin`, `stdout`, `stderr`. The last is unbuffered
and separate on purpose — diagnostics still appear when stdout is redirected to
a file, and they do not pollute the data.

## Reading

```c
char line[256];
while (fgets(line, sizeof line, f) != NULL) { ... }
```

`fgets` takes the buffer size and will not exceed it. It **keeps** the trailing
newline, which surprises people — strip it if you do not want it. Its ancient
counterpart `gets` had no size parameter, could not be used safely, and was
removed from the language in C11.

`fgetc` returns an `int`, not a `char`, because it must be able to return `EOF`
as a value no character can be. Storing it in a `char` breaks the comparison on
platforms where `char` is signed.

## Check everything

Almost every C standard library function reports failure through its return
value, and almost every C program ignores it:

| Call | Failure |
|---|---|
| `fopen` | `NULL` |
| `fgets` | `NULL` at EOF *or* on error |
| `fclose` | non-zero — yes, closing can fail |
| `fprintf` | negative |
| `malloc` | `NULL` |

`fclose` failing is not theoretical: buffered data is flushed there, so a full
disk surfaces at close rather than at write. A program that writes a file and
does not check `fclose` can report success having written nothing.

`feof` is only true *after* a read has already failed, so `while (!feof(f))` is
a classic bug — it runs one extra iteration with stale data. Loop on the read
itself.

## Your turn

In `io.h` and `io.c`:

- `int write_lines(const char *path, const char **lines, int n)` — one per
  line, returns the count written or -1
- `int count_lines(const char *path)` — or -1 if it cannot be opened
- `int read_first_line(const char *path, char *buf, int size)` — without the
  newline, returns the length or -1
- `int append_line(const char *path, const char *line)` — 0 or -1
