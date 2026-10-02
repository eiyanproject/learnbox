---
title: File types and magic bytes
summary: A file's real type is in its first few bytes, not its name - and an attacker counts on you trusting the name.
order: 2
files: [filetype.py]
run: python filetype.py
hints:
  - "`identify`: compare the start of the data against each known magic signature; return the first that matches, or 'unknown'."
  - "The signatures are given to you in `MAGICS`. A file starts with its magic, so `data.startswith(sig)`."
  - "`extension_mismatch`: work out the real type from the magic, and the claimed type from the filename's extension; if the file is a known type that disagrees with its extension, that is a mismatch."
  - "A `.jpg` whose bytes are really an ELF executable is the classic disguised-malware case."
---

The name of a file is a label anyone can write; its **type** is in its bytes.
Nearly every format begins with a fixed **magic number** - a signature that
identifies it regardless of the extension. This is how the `file` command knows
what something is, and how you catch a file pretending to be something it is
not.

## Common signatures

| Type | First bytes |
|---|---|
| PNG | `89 50 4E 47 0D 0A 1A 0A` |
| PDF | `%PDF` |
| ELF (Linux executable) | `7F 45 4C 46` |
| ZIP / docx / jar | `50 4B 03 04` (`PK..`) |
| JPEG | `FF D8 FF` |
| GZIP | `1F 8B` |

## Why it matters

An attacker renames a malicious executable `invoice.pdf` or `photo.jpg` and
relies on you trusting the extension - the system, or the user, runs it as what
it claims to be. A file whose magic says ELF but whose name says `.jpg` is a
red flag that needs no further analysis to raise. Checking the bytes against the
name is a cheap, high-value triage step, and it is the first thing automated
scanners do.

## Your turn

`MAGICS` (signatures) and `EXT_TYPES` (extension-to-type) are provided. In
`filetype.py`:

- `identify(data)` - the type name from the magic bytes, or `"unknown"`
- `extension_mismatch(filename, data)` - `True` when the file is a recognised
  type that does not match its extension
