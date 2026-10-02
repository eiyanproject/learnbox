---
title: Reading bytes
summary: The tools that show you what a file really contains - and what strings, hexdump and the rest are doing underneath.
order: 2
files: [byteview.py]
run: python byteview.py
hints:
  - "`hexdump`: step through the data 16 bytes at a time. For each chunk, format the offset with `f\"{offset:08x}\"`, each byte with `f\"{b:02x}\"`, and the ASCII column with the byte as a character when `32 <= b < 127`, else a dot."
  - "`find_strings`: walk the bytes, collecting runs of printable characters (32..126); when a run ends, keep it if it is at least `min_len` long."
  - "A byte is printable here if `32 <= b <= 126`. Reset the current run on any other byte."
---

A security person spends more time **reading** files than attacking them, and
most interesting files are not text. A captured packet, a compiled program, a
memory dump - open them in a normal editor and you get garbage, because the
editor is guessing they are text and they are not.

Three tools show you what is really there. You will use the real ones later;
understanding them means knowing what they do underneath.

## strings

`strings file` prints the runs of readable text buried in a binary. It is the
first thing to run on anything unknown: a program's error messages, URLs,
embedded passwords and file paths are all plain text sitting in the binary, and
`strings` drags them into the light.

```text
$ strings mystery.bin
/bin/sh
GCC: (Debian 14.2.0)
password123
```

The rule is simple: a run of printable bytes (roughly space through `~`, bytes
32 to 126) that is long enough to be deliberate rather than accidental.

## hexdump

`xxd file` shows every byte as hex, with an ASCII column beside it:

```text
00000000: 7f45 4c46 0201 0100 0000 0000 0000 0000  .ELF............
00000010: 0300 3e00 0100 0000 5010 0000 0000 0000  ..>.....P.......
```

Three columns: the **offset** (where in the file you are), the **bytes** as
hex, and the **ASCII** rendering with a dot for anything unprintable. Those
first four bytes - `7f 45 4c 46`, which read as `.ELF` - are a **magic number**,
the fingerprint that says "this is a Linux executable" no matter what the file
is named.

## od, and why hex

`od -A x -t x1z` does the same job with different defaults. Hex is the common
language because one byte is exactly two hex digits, so the columns always line
up and you can see structure - repeats, padding, boundaries - at a glance.

## Your turn

Reimplement the core of two of these tools, in `byteview.py`:

- `hexdump(data)` - a string of `xxd`-style lines: an 8-digit hex offset, up to
  16 space-separated two-digit hex bytes, two spaces, then the ASCII column
  (the byte as a character when printable, a `.` otherwise). One line per 16
  bytes; the last line may be short. (For this exercise do not pad the hex
  columns on a short final line - just the bytes that are there.)
- `find_strings(data, min_len=4)` - a list of the printable runs at least
  `min_len` bytes long, in order, as strings
