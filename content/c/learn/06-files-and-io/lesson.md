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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **stream** | a source or destination of bytes, such as a file |
| **`FILE *`** | an opaque handle to a buffered stream |
| **opaque** | you use it only through functions, never look inside |
| **buffered** | data collected in memory and written in larger pieces |
| **flush** | write buffered data out; happens at `fclose` |
| **mode** | how a file is opened: `"r"`, `"w"`, `"a"`, `"r+"`, `"w+"`, plus `"b"` |
| **truncate** | empty a file when opening it |
| **append** | add to the end |
| **`stdin`**, **`stdout`**, **`stderr`** | the three streams every program has; `stderr` is unbuffered |
| **redirect** | send a program's output to a file instead of the screen |
| **EOF** | end of file |
| **`errno`** | a global number saying why the last call failed |
| **return value check** | the way almost every C library function reports failure |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall io.c -o io && ./io` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `fopen(path, "r")` | opens a file; `NULL` on failure |
| `fclose(f)` | closes it; non-zero on failure, such as a full disk |
| `fgets(line, sizeof line, f)` | reads one line, keeping the newline; `NULL` at EOF or error |
| `fputs(s, f)`, `fprintf(f, ...)` | write text |
| `fgetc(f)` | reads one character as an `int`, so `EOF` fits |
| `feof(f)` | true only after a read has failed: never loop on it |
| `tmpfile()` | a scratch file deleted on close |
| `rewind(f)` | goes back to the start |
| `gets` | removed in C11: it could not be used safely |

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
newline, which surprises people — strip it if you do not want it. The brackets
show exactly what each call returned:

```c
#include <stdio.h>

int main(void) {
    FILE *f = tmpfile();               /* a scratch file, deleted on close */
    if (f == NULL) return 1;
    fputs("first\nsecond\n", f);
    rewind(f);

    char line[256];
    while (fgets(line, sizeof line, f) != NULL) {
        printf("[%s]", line);
    }
    if (fclose(f) != 0) return 1;
    return 0;
}
```

```output
[first
][second
]
```

The ancient counterpart of `fgets`, `gets`, had no size parameter, could not
be used safely, and was removed from the language in C11.

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
