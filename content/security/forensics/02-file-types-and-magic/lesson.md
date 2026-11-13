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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **file name** | a label anyone can choose; it says nothing reliable about the contents |
| **extension** | the part of the name after the last dot: `.jpg`, `.pdf` |
| **file type** (format) | how the bytes are actually laid out: a PNG image, a PDF, a program |
| **magic number** (magic bytes, signature) | fixed first bytes that identify a format, whatever the name |
| **libmagic** | the library of signatures behind the `file` command |
| **ELF** | the format of Linux programs; starts with `7f 45 4c 46` (`.ELF`) |
| **PNG**, **JPEG** | image formats; `89 50 4e 47 ...` and `ff d8 ff` |
| **PDF** | document format; starts with the text `%PDF` |
| **ZIP** | archive format, `PK\x03\x04`; `.docx`, `.xlsx` and `.jar` files are ZIPs inside |
| **GZIP** | compressed format, `1f 8b`; `.gz` and `.tar.gz` |
| **disguised file** | one whose name claims a different type from its bytes |
| **mismatch** | the type from the bytes and the type from the extension disagree |
| **triage** | a quick first check to decide what needs a closer look |
| **red flag** | a sign that something is wrong and needs looking into |
| **heuristic** | a rule of thumb that is usually right; `file` can be fooled by a crafted file |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `file name` | names the file's real type from its magic bytes |
| `head -c 4 name \| od -A x -t x1z` | shows the first four bytes in hex with characters |
| `python filetype.py` | runs your program: identifies an ELF and checks a disguised `.jpg` |

### Python names

| Name | What it does |
|---|---|
| `MAGICS` | given to you: a list of `(signature bytes, type name)` pairs |
| `EXT_TYPES` | given to you: a dict from extension to the type it claims |
| `b"\x89PNG\r\n\x1a\n"` | a bytes literal mixing hex bytes (`\x89`) and characters |
| `data.startswith(sig)` | `True` when the data begins with those bytes |
| `filename.rsplit(".", 1)[-1]` | the part after the last dot |
| `.lower()` | lowercase, so `.JPG` counts as `.jpg` |
| `EXT_TYPES.get(ext)` | the claimed type, or `None` for an extension not in the table |
| `claimed is not None and claimed != real` | an extension we know, which disagrees with the bytes |

---

A file's name is a label anyone can write. Its **type** is in its bytes.
Nearly every format begins with fixed **magic bytes**, a signature that
identifies it whatever the extension says. That is how the `file` command
knows what something is, and how you catch a file pretending to be something
it is not.

## Common signatures

| Type | First bytes (hex) | As characters |
|---|---|---|
| PNG image | `89 50 4E 47 0D 0A 1A 0A` | `.PNG....` |
| PDF document | `25 50 44 46` | `%PDF` |
| ELF (Linux program) | `7F 45 4C 46` | `.ELF` |
| ZIP, docx, xlsx, jar | `50 4B 03 04` | `PK..` |
| JPEG image | `FF D8 FF` | |
| GZIP | `1F 8B` | |

You met the ELF one in Environment lesson 2. Office files (`.docx`, `.xlsx`)
and Java `.jar` files are ZIP archives inside, so they share ZIP's signature.

## A disguised file

Here a Linux program has been copied to a file called `photo.jpg`. The name
says "picture". The bytes say otherwise:

```text
$ file photo.jpg
photo.jpg: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), ...
$ head -c 4 photo.jpg | od -A x -t x1z
000000 7f 45 4c 46                                      >.ELF<
```

`file` ignores the name and reads the magic bytes: this is a program.

## Why it matters

An attacker renames a malicious program `invoice.pdf` or `photo.jpg` and relies
on people, or software, trusting the extension. A file whose bytes say ELF but
whose name says `.jpg` is a **red flag** before any deeper analysis. Comparing
the bytes with the name is a cheap, valuable **triage** step, and it is one of
the first things automated scanners do.

Two limits, from the Trail of Bits forensics guide:

- `file` is a **heuristic** and can be fooled by a file built to confuse it.
- It sees only the outside. A file hidden **inside** another one is not
  reported; that is what Forensics lessons 4 and 5 are about.

## Your turn

`MAGICS` (signatures) and `EXT_TYPES` (extension to type) are given to you. In
`filetype.py`:

- `identify(data)`: the type name from the magic bytes, or `"unknown"`.
- `extension_mismatch(filename, data)`: `True` when the file is a recognised
  type **and** its extension is one in `EXT_TYPES` that claims a different
  type. An unknown type, or an extension not in the table, is not a
  mismatch.

```pycon
>>> from filetype import identify, extension_mismatch
>>> identify(b"%PDF-1.7")
'pdf'
>>> extension_mismatch("report.pdf", b"%PDF-1.7")
False
>>> extension_mismatch("invoice.jpg", b"\x7fELF...")
True
```

Run it:

```text
elf
disguised? True
```

## Check yourself

1. Where does `file` get a file's type from?
   *Its magic bytes, not its name.*
2. What are the first four bytes of a Linux program?
   *`7f 45 4c 46`: `.ELF`.*
3. A `.docx` file starts with `PK`. Is that suspicious?
   *No: `.docx` files are ZIP archives.*
4. Why is an ELF file named `.jpg` a red flag?
   *A program is pretending to be a picture, so someone may run it.*
5. What can `file` miss?
   *A file hidden inside another file, or one crafted to fool it.*
