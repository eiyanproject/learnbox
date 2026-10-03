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

A compiled program looks like noise in a text editor, but it is a precisely
structured file. On Linux that structure is **ELF** (Executable and Linkable
Format), and reading its header is the first thing any analysis does - it says
what the thing is before you ever run it. (Running an unknown binary is the last
resort, and never on a machine you care about; reading it is safe.)

## The ELF header

The file opens with a 16-byte **identification** followed by fields describing
the whole binary:

- bytes 0-3: the magic `\x7fELF` - the fingerprint from the very first lesson
- byte 4: **class** - 1 for 32-bit, 2 for 64-bit
- byte 5: **data** - 1 for little-endian, 2 for big
- offset 16: **type** - REL (1, an object file), EXEC (2, a fixed-address
  executable), DYN (3, a shared library or position-independent executable)
- offset 18: **machine** - `0x3E` is x86-64, `0xB7` is AArch64
- offset 24: **entry point** - the address where execution begins

## Why the type matters

`EXEC` against `DYN` is a security-relevant distinction. A **position-independent
executable** (PIE, type DYN) can be loaded at a random base address every run,
which is what makes **address-space layout randomisation** effective against
exploitation. A non-PIE `EXEC` always loads at the same address - easier to
attack. Spotting which you have is step one of assessing a binary's defences.

This is what `readelf -h` and `file` report; you are building their core.

## Your turn

`SAMPLE_ELF` is provided in `elf_data.py`. In `elf.py`:

- `parse_elf(data)` - `{magic_ok, bits, endian, type, machine, entry}`:
  `magic_ok` a bool, `bits` the integer `32` or `64`, `endian` the string
  `"little"` or `"big"`, `type` the name `"REL"`, `"EXEC"` or `"DYN"`, `machine`
  `"x86-64"` or `"AArch64"`, and `entry` an integer. The multi-byte fields are
  little-endian in this exercise, and `entry` is the 64-bit form at offset 24.
  When the magic is wrong, only `magic_ok` (`False`) has to be right
- `is_executable(data)` - `True` for an EXEC or DYN type
- `is_pie(data)` - `True` for a position-independent executable (type DYN)
