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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **byte** | the smallest unit of a file: a number from 0 to 255, eight bits |
| **bit** | one binary digit, 0 or 1 |
| **binary file** | a file that is not text: a program, a picture, a packet capture, a memory dump |
| **text file** | a file whose bytes are all readable characters |
| **printable byte** | one that shows as a character: 32 (space) up to 126 (`~`) |
| **ASCII** | the standard numbering of characters: `A` is 65, space is 32 |
| **hexadecimal** (hex) | base 16, digits `0-9` and `a-f`; one byte is exactly two hex digits (`ff` is 255) |
| **octal** | base 8; `od` can show bytes this way |
| **offset** | how far into the file a byte is, counted from 0, usually in hex |
| **hex dump** | every byte as hex, with offsets and an ASCII column beside |
| **ASCII column** | the bytes shown as characters, with a `.` for anything unprintable |
| **run of printable bytes** | readable bytes next to each other: the text `strings` looks for |
| **magic number** (file signature) | fixed first bytes that say what a file is, whatever its name: `7f 45 4c 46` (`.ELF`) for a Linux program |
| **ELF** | the file format of Linux programs |
| **triage** | a first quick look at something unknown, to decide what it is |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `strings file` | prints the runs of at least 4 printable bytes |
| `strings -n 3 file` | the same, for runs of at least 3 |
| `xxd file` | a hex dump, bytes in pairs (`7f45`) |
| `xxd -g1 file` | a hex dump, one byte at a time (`7f 45`) |
| `od -A x -t x1z file` | a hex dump with hex offsets (`-A x`), single bytes in hex (`-t x1`) and characters (`z`) |
| `file name` | guesses a file's type from its magic number |

### Python names

| Name | What it does |
|---|---|
| `b"\x7fELF"` | a bytes literal; `\x7f` is the byte 0x7f |
| `for b in data:` | each byte of a bytes object, as an int |
| `f"{b:02x}"` | a byte as two lowercase hex digits |
| `f"{offset:08x}"` | an offset as eight hex digits |
| `chr(65)`, `ord("A")` | the character for a number; the number for a character |
| `data[i:i + 16]` | the next 16 bytes |
| `"\n".join(lines)` | lines joined with newlines |

---

A security person spends more time **reading** files than attacking them, and
most interesting files are not text. A captured network packet, a compiled
program, a memory dump: open one in a normal editor and you get garbage,
because the editor assumes the bytes are characters, and they are not.

Every file is a sequence of **bytes**, numbers from 0 to 255. Some of those
numbers stand for characters in **ASCII**, the standard numbering: 65 is
`A`, 32 is a space, 126 is `~`. The bytes from 32 to 126 are the
**printable** ones; the rest are control codes or have no character at all.

```pycon
>>> ord("A"), chr(65), hex(65)
(65, 'A', '0x41')
>>> bytes([72, 105])
b'Hi'
```

Three standard tools show you what is really in a file. You will use the
real ones later; in this lesson you build the core of two of them, so you
know exactly what they do underneath.

## strings: the readable parts

`strings file` prints the runs of readable text buried in a binary file. It
is the first thing to run on anything unknown: a program's error messages,
URLs, embedded passwords and file paths are plain text sitting inside the
binary, and `strings` drags them into the light.

The rule is simple: a run of printable bytes (32 to 126) next to each other,
long enough to be deliberate rather than accidental. By default "long
enough" is **4**, because any binary is full of 1-, 2- and 3-byte runs that
happen to be printable by chance. For a small file holding
`Hi`, two unprintable bytes, `password123`, one more unprintable byte and
`end`:

```text
$ strings mystery.bin
password123
$ strings -n 3 mystery.bin
password123
end
```

`Hi` is too short to count, and `end` only appears once the minimum is
lowered to 3 with `-n`.

## A hex dump: every byte

`xxd` shows every byte as **hexadecimal** (base 16, digits `0-9` then
`a-f`). Hex is the common language for bytes because one byte is exactly two
hex digits, from `00` to `ff`, so the columns always line up and you can see
structure (repeats, padding, boundaries) at a glance. `xxd -g1` prints one
byte per group, which is the layout you will build. The same file:

```text
$ xxd -g1 mystery.bin
00000000: 48 69 00 01 70 61 73 73 77 6f 72 64 31 32 33 ff  Hi..password123.
00000010: 65 6e 64                                         end
```

Three columns:

1. the **offset**: where in the file this line starts, in hex. The second
   line starts at `0x10`, which is 16, because each line holds 16 bytes.
2. the **bytes**, as two hex digits each: `48` is 72, `H`.
3. the **ASCII column**: each byte as its character, with a `.` for
   anything unprintable, such as `00`, `01` and `ff` here.

Plain `xxd`, without `-g1`, groups the bytes in pairs (`4869 0001 ...`).
`od -A x -t x1z` does the same job with different defaults: `-A x` shows
offsets in hex, `-t x1` single bytes in hex, and `z` adds the characters:

```text
$ od -A x -t x1z mystery.bin
000000 48 69 00 01 70 61 73 73 77 6f 72 64 31 32 33 ff  >Hi..password123.<
000010 65 6e 64                                         >end<
000013
```

(The last line is the total length, 0x13 = 19 bytes.)

## Magic numbers

The first bytes of most file formats are fixed, a **magic number** (or file
signature) that says what the file is, whatever it is named. A Linux program
(the **ELF** format) always starts with `7f 45 4c 46`, which reads as
`.ELF` in the ASCII column:

```pycon
>>> from byteview import hexdump
>>> print(hexdump(b"\x7fELF\x02\x01\x01\x00"))
00000000: 7f 45 4c 46 02 01 01 00  .ELF....
```

(That is the solution's `hexdump`, the function you are about to write.)
The `file` command reads these signatures to guess a type. The Forensics
section uses them to catch a file whose name lies about what it is.

## Your turn

In `byteview.py`, write:

- `hexdump(data)`: a string of `xxd -g1`-style lines, one per 16 bytes:
  - the offset as 8 lowercase hex digits, a colon and a space;
  - the bytes (up to 16) as two lowercase hex digits each, separated by single
    spaces. Do **not** pad a short last line to full width: only the bytes
    that are there;
  - two spaces, then the ASCII column (the byte's character when it is 32 to
    126, otherwise `.`).

  Join the lines with `\n`, with no newline after the last one. Empty data
  gives `""`. `hexdump(b"\x00\xff")` is `"00000000: 00 ff  .."`.
- `find_strings(data, min_len=4)`: a list of the printable runs (bytes 32 to
  126) at least `min_len` long, in order, as **strings** (not bytes). A run
  at the very end of the data counts too.
  `find_strings(b"\x00ok\x00longer\x00")` is `["longer"]`.
