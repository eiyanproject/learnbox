---
title: Strings and symbols
summary: Before any disassembly, the readable text and the symbol table tell you most of what a binary does.
order: 2
files: [symbols.py]
run: python symbols.py
hints:
  - "`extract_strings`: collect runs of printable bytes (32..126) at least `min_len` long - the same idea as the environment lesson."
  - "`find_symbol`: the symbol table is a list of `(name, address)`; return the address for a name, or None."
  - "`imported_danger`: return the subset of symbol names that are in the `RISKY` set - library functions worth a closer look."
  - "A binary that imports `system` and `gets` is telling you where to look before you read a single instruction."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **string** (in a binary) | readable text stored inside the program: messages, paths, commands |
| **printable byte** | a byte from 32 (space) to 126 (`~`) |
| **hard-coded secret** | a password or key written into the program itself; `strings` finds it |
| **format string** | text with placeholders such as `%s`, used by `printf` |
| **symbol** | a name for a function or variable, with its address |
| **symbol table** | the list of a binary's symbols |
| **import** | a function the program uses from a library, found when it starts |
| **library** | shared code many programs use, such as the C library (`libc`) |
| **`libc`** | the standard C library; `system`, `gets`, `strcpy` and `printf` live there |
| **capability** | something the program can do: talk on the network, run commands, read files |
| **risky function** | a library function that is often the site of a bug when misused |
| **`system`**, **`popen`**, **`exec`** | run another program; dangerous if the command includes user input (Web lesson 6) |
| **`gets`** | reads a line with **no length limit**; so unsafe it was removed from the C standard |
| **`strcpy`**, **`strcat`**, **`sprintf`**, **`scanf`** | copy or format text with no check on the destination's size |
| **stripped binary** | one with its own symbol names removed; its imports still show |
| **triage** | a quick first look to decide where to dig |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `strings -n 6 file` | prints runs of at least 6 printable bytes |
| `nm -D file` | lists the dynamic symbols: `U` means imported (undefined here) |
| `readelf -s file` | lists every symbol with its address |
| `gcc -o name name.c` | compiles a C file into a program |
| `python symbols.py` | runs your program: finds the risky imports in a symbol list |

### Python names

| Name | What it does |
|---|---|
| `RISKY` | given to you: the set of risky function names |
| `32 <= b <= 126` | `True` for a printable byte |
| `run.append(chr(b))` | adds the character to the current run |
| `"".join(run)` | the run as one string |
| `found, run = [], []` | two empty lists at once |
| `(name, address)` | one symbol |
| `for sym_name, addr in symbols:` | each symbol, taken apart |
| `{name for name, _ in symbols if name in RISKY}` | the set of symbol names that are also in `RISKY` |
| `0x401050` | an address, written in hex |

---

Reverse engineering does not start with disassembly. It starts with the two
cheapest sources of information in any binary: the **strings** it contains,
and the **symbols** it uses. Together they often reveal what the program does,
and where it is weak, before you read a single instruction.

## A small example

Here is a tiny C program that makes a backup by running `tar`:

```c
#include <stdio.h>
#include <stdlib.h>
int main(void) {
    puts("starting backup");
    return system("tar czf /tmp/backup.tgz /etc/app.conf");
}
```

Pretend you have only the compiled file, not this source. Two commands
already tell most of the story.

## Strings

Messages, file paths, web addresses, commands, and sometimes **hard-coded
secrets** are stored in the binary as plain text. `strings`, which you built in
Environment lesson 2, pulls them out:

```text
$ strings -n 6 backup | grep -E 'backup|tar|app'
starting backup
tar czf /tmp/backup.tgz /etc/app.conf
```

Without any other information you now know the program prints a message,
runs `tar`, and touches `/etc/app.conf`.

## Symbols

The **symbol table** names functions: the program's own, and the library
functions it **imports**. `nm -D` lists the imported ones, marked `U`
("undefined here, found in a library at start-up"):

```text
$ nm -D backup
                 U __libc_start_main@GLIBC_2.34
                 U puts@GLIBC_2.2.5
                 U system@GLIBC_2.2.5
```

The import list is a map of the program's **capabilities**:

| If it imports | It can |
|---|---|
| `socket`, `connect` | talk on the network |
| `open`, `read`, `write` | read and write files |
| `system`, `popen`, `exec...` | run other programs, and so possibly shell commands |
| `gets`, `strcpy`, `sprintf` | copy text with no size check: a likely buffer overflow |

This one imports `system`, so the question to ask is: can any user input end
up in that command? That is Web lesson 6's command injection, in compiled form.

A program can have its own function names removed (a **stripped** binary),
but its imports must stay, because the system needs them to start it. So the
import list is almost always there to read.

Imports of the risky functions are where reviewers look first. `gets` reads a
line of any length into a fixed-size space, which is so dangerous it was
removed from the C language standard. The next lessons show what goes wrong.

## Your turn

`RISKY`, a set of dangerous imports, is given to you. In `symbols.py`:

- `extract_strings(data, min_len=4)`: the runs of printable bytes (32 to 126)
  at least `min_len` long, in order, as strings. This is the `strings` tool
  from the Environment section.
- `find_symbol(symbols, name)`: the address for a symbol name, or `None`.
  `symbols` is a list of `(name, address)`.
- `imported_danger(symbols)`: the set of symbol names that are in `RISKY`.

Run it:

```text
risky imports: {'gets'}
```

## Check yourself

1. What does `U` mean in `nm -D` output?
   *The symbol is imported: defined in a library, not in this file.*
2. A binary imports `socket` and `connect`. What can it do?
   *Make network connections.*
3. Why is `system` in the risky set?
   *It runs a shell command; user input in it means command injection.*
4. What is wrong with `gets`?
   *It has no length limit, so it can write past the end of its buffer.*
5. Why does a stripped binary still show its imports?
   *The system needs them to load the library functions at start-up.*
