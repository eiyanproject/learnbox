---
title: What a binary is
summary: A compiled program is a structured file, not noise. Parsing its ELF header tells you what it is before you run anything.
order: 1
files: [elf.py]
run: python elf.py
hints:
  - "The first four bytes are the magic `\\x7fELF`. Byte 4 is the class (1 = 32-bit, 2 = 64-bit); byte 5 is the endianness (1 = little)."
  - "After the 16-byte identification come two 16-bit fields: type (at offset 16) and machine (at offset 18), both little-endian."
  - "The entry point - where execution begins - is the 8-byte value at offset 24 for a 64-bit ELF."
  - "`is_pie`: a position-independent executable has type DYN (3) rather than EXEC (2)."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **binary** (compiled program) | a program turned from source code into machine instructions, stored as a file |
| **compiler** | the program that does that translation, such as `gcc` |
| **reverse engineering** (reversing) | working out what a program does from the binary, without its source code |
| **static analysis** | studying a file without running it; safe |
| **dynamic analysis** | running it to watch what it does; only in an isolated machine |
| **ELF** | Executable and Linkable Format: the file format of Linux programs and libraries |
| **ELF header** | the first 64 bytes (on 64-bit), describing the whole file |
| **identification** (`e_ident`) | the first 16 bytes: magic, class, data and a few more |
| **class** | byte 4: 1 for 32-bit, 2 for 64-bit |
| **data** (endianness) | byte 5: 1 for little-endian, 2 for big-endian |
| **little-endian** | least significant byte first; x86-64 and most ARM machines use it |
| **type** | offset 16: REL (1), EXEC (2) or DYN (3) |
| **REL** | an object file: compiled, but not yet linked into a program |
| **EXEC** | an executable that always loads at the same fixed address |
| **DYN** | a shared library, or a position-independent executable |
| **machine** | offset 18: which processor it is for; `0x3E` is x86-64, `0xB7` is AArch64 |
| **x86-64**, **AArch64** | the 64-bit processor families of most PCs and of most phones and newer Macs |
| **entry point** | offset 24: the address where the program starts running |
| **address** | a position in the program's memory |
| **PIE** (position-independent executable) | a program that can be loaded at any address; type DYN |
| **ASLR** (address space layout randomisation) | loading programs and libraries at a random address every run, so attackers cannot predict where code is |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `readelf -h file` | prints the ELF header, field by field |
| `file file` | one-line summary: class, type, machine and more |
| `python elf.py` | runs your program: parses the sample ELF and says whether it is PIE |

### Python names

| Name | What it does |
|---|---|
| `SAMPLE_ELF` | given to you in `elf_data.py`: the first bytes of an ELF file |
| `TYPES`, `MACHINES` | given to you: dicts from numbers to names |
| `data[:4] == b"\x7fELF"` | `True` when the magic is right |
| `data[4]`, `data[5]` | single bytes, as numbers |
| `struct.unpack("<H", data[16:18])[0]` | a 2-byte little-endian number (`<` little-endian, `H` 2 bytes) |
| `int.from_bytes(data[24:32], "little")` | an 8-byte little-endian number |
| `TYPES.get(e_type, "?")` | the name, or `"?"` for a number not in the dict |
| `hex(n)` | a number written in hex, `'0x401050'` |

---

A compiled program looks like garbage in a text editor, but it is a precisely
structured file. On Linux the structure is **ELF** (Executable and Linkable
Format), and reading its header is the first step of any analysis: it tells
you what the thing is before you ever run it.

**Reading** a binary (static analysis) is safe. **Running** an unknown one is
the last resort, and only on a throwaway, isolated machine, never on one you
care about.

## The ELF header

The file opens with a 16-byte **identification**, followed by fields that
describe the whole binary. The ones this lesson reads:

| Offset | Size | Field | Values |
|---|---|---|---|
| 0 | 4 | magic | `7f 45 4c 46`, `.ELF`: the signature from Environment lesson 2 |
| 4 | 1 | class | 1 = 32-bit, 2 = 64-bit |
| 5 | 1 | data | 1 = little-endian, 2 = big-endian |
| 16 | 2 | type | 1 = REL (object file), 2 = EXEC (fixed address), 3 = DYN (library or PIE) |
| 18 | 2 | machine | `0x3E` = x86-64, `0xB7` = AArch64 |
| 24 | 8 | entry point | the address where execution starts (4 bytes on 32-bit) |

In this exercise the multi-byte fields are **little-endian**: the least
significant byte comes first, as on every x86-64 machine.

`readelf -h` prints the same fields. Here it is on `/usr/bin/true`, a real
program on this machine:

```text
$ readelf -h /usr/bin/true
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  ...
  Type:                              DYN (Position-Independent Executable file)
  Machine:                           Advanced Micro Devices X86-64
  ...
  Entry point address:               0x2590
```

Read the magic line against the table: `02` at byte 4 is 64-bit, `01` at byte
5 is little-endian.

## Why the type matters

The difference between EXEC and DYN matters for security.

- A **position-independent executable** (PIE, type DYN) can be loaded at a
  different, random address every time it runs. That is what makes **ASLR**,
  address space layout randomisation, work: an attacker who finds a bug cannot
  know in advance where the program's code will be in memory.
- A non-PIE **EXEC** always loads at the same address, so its code is always in
  the same place. That makes attacks easier.

Modern compilers build PIE by default; the `/usr/bin/true` above is one. The
lesson's sample is an EXEC, with its entry point at the fixed address
`0x401050`. Telling which you have is step one of assessing a binary's
defences, and Reversing lesson 5 comes back to it.

## Your turn

`SAMPLE_ELF` is given to you in `elf_data.py`. In `elf.py`:

- `parse_elf(data)`: a dict `{magic_ok, bits, endian, type, machine, entry}`:
  - `magic_ok`: a bool;
  - `bits`: the integer `32` or `64`;
  - `endian`: the string `"little"` or `"big"`;
  - `type`: `"REL"`, `"EXEC"` or `"DYN"`;
  - `machine`: `"x86-64"` or `"AArch64"`;
  - `entry`: an integer, the 64-bit form at offset 24.

  The multi-byte fields are little-endian. When the magic is wrong, only
  `magic_ok` (`False`) has to be right.
- `is_executable(data)`: `True` for type EXEC or DYN.
- `is_pie(data)`: `True` for a position-independent executable (type DYN).

Run it:

```text
{'magic_ok': True, 'bits': 64, 'endian': 'little', 'type': 'EXEC', 'machine': 'x86-64', 'entry': 4198480}
PIE? False
```

(`4198480` is `0x401050`.)

## Check yourself

1. Byte 4 of an ELF file is `02`. What does it mean?
   *A 64-bit binary.*
2. What is the entry point?
   *The address where the program starts running.*
3. What type is a position-independent executable?
   *DYN (3).*
4. Why does PIE help against attacks?
   *It can be loaded at a random address, so ASLR hides where its code is.*
5. Why read a binary rather than run it?
   *Reading is safe; running an unknown program can harm the machine.*
