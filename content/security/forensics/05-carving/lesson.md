---
title: Carving a file out of a blob
summary: Recovering a file from raw bytes - a disk image, a memory dump - by finding where it starts and where it ends.
order: 5
files: [carve.py]
run: python carve.py
hints:
  - "A PNG starts with the 8-byte signature and ends at the IEND chunk plus its 4-byte CRC."
  - "`carve_png`: find the signature with `.find`, find `IEND` after it, and return from the signature to 8 bytes past the start of IEND (the `IEND` type is 4 bytes, its CRC another 4)."
  - "Return `None` when there is no complete PNG - no signature, or no IEND after it."
  - "This is file carving: recovering a file by its structure alone, with no filesystem to tell you where it is."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **file system** | the part of the operating system that records which bytes on a disk belong to which file |
| **directory entry** | the record of a file's name and where its bytes are |
| **deleted file** | its directory entry is gone, but its bytes often stay on the disk until something overwrites them |
| **blob** | a run of raw bytes with no known structure: a disk image, a memory dump |
| **disk image** | a byte-for-byte copy of a whole disk or memory card |
| **memory dump** | a copy of a computer's memory at one moment |
| **file carving** | recovering files from a blob by their structure alone, with no file system |
| **header** (start signature) | the bytes a format always begins with |
| **footer** (end marker) | the bytes a format always ends with |
| **header-to-footer scan** | find a header, find the next footer after it, cut out what is between |
| **IEND + CRC** | the end of a PNG: the letters `IEND` and 4 more bytes |
| **`FF D8` ... `FF D9`** | the start and end markers of a JPEG |
| **offset** | a position in the blob, counted in bytes from 0 |
| **junk** | the unrelated bytes around the file |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `dd if=blob.bin of=out.png bs=1 skip=37 count=69` | copies 69 bytes, starting 37 bytes in, from `blob.bin` into `out.png` |
| `binwalk blob.bin` | scans a blob for known file signatures and lists their offsets |
| `foremost`, `scalpel` | tools that carve every file type they know from a disk image |
| `file out.png` | confirms what the carved bytes are |
| `python carve.py` | runs your program: carves the PNG out of the sample blob |

### Python names

| Name | What it does |
|---|---|
| `CARVE_BLOB` | given to you in `forensics_data.py`: a PNG buried in junk |
| `PNG_SIG` | given to you: the 8-byte PNG signature |
| `blob.find(PNG_SIG)` | the offset of the first signature, or `-1` |
| `blob.find(b"IEND", start)` | the offset of the first `IEND` at or after `start` |
| `iend + 4 + 4` | the offset just past `IEND` and its CRC |
| `blob[start:end]` | the bytes from `start` up to (not including) `end` |

---

When you delete a file, the **file system** forgets where its bytes are, but
the bytes themselves usually stay on the disk until something overwrites
them. **File carving** gets them back without any help from the file system:
scan the raw bytes for the **header** and **footer** of a known format, and
cut out everything between. It is how deleted photos are recovered from a
memory card, and how files are pulled out of a **memory dump** or a **disk
image**.

## Start and end

A format you can carve has a recognisable start and a recognisable end:

| Format | Starts with | Ends with |
|---|---|---|
| PNG | the 8-byte signature `89 50 4E 47 0D 0A 1A 0A` | the `IEND` chunk type plus its 4-byte CRC |
| JPEG | `FF D8` | `FF D9` |
| PDF | `%PDF` | `%%EOF` |

The method is a **header-to-footer scan**:

1. Find the header in the blob.
2. Find the first footer **after** it.
3. The bytes from the start of the header to the end of the footer are the
   file.

Everything around it is junk that happens to share the disk.

## Doing it by hand

The lesson's blob is 123 bytes. Searching it finds the PNG signature at
offset 37, and `IEND` at offset 98. The file therefore ends 8 bytes after
that, at offset 106: 69 bytes in all. The classic tool for cutting out a
range of bytes is `dd`:

```text
$ dd if=blob.bin of=out.png bs=1 skip=37 count=69
69+0 records in
69+0 records out
69 bytes copied, 0.000123674 s, 558 kB/s
$ file out.png
out.png: PNG image data, 2 x 2, 8-bit/color RGB, non-interlaced
```

`if` is the input file, `of` the output, `bs=1` says to count in single bytes,
`skip=37` jumps to the start and `count=69` takes the file's length. `file`
confirms the result is a real PNG.

Tools such as `binwalk` (for firmware and blobs) and `foremost` or `scalpel`
(for disk images) do this scan for hundreds of formats at once. Your
`carve_png` is the same idea for one format.

A carved file is not always whole. If part of it was overwritten, or its
pieces were not next to each other on the disk, the cut-out bytes are
damaged. Real carving tools check each result, as `file` did here.

## Your turn

`CARVE_BLOB`, a PNG buried in junk, is given to you in `forensics_data.py`. In
`carve.py`:

- `carve_png(blob)`: the exact bytes of the PNG inside the blob, from the first
  byte of its signature through the 4-byte CRC that follows `IEND`. Return
  `None` if there is no complete PNG: no signature, or no `IEND` after it.

Run it:

```text
carved 69 bytes
```

## Check yourself

1. Why can a deleted file often be recovered?
   *Its bytes stay on the disk until something overwrites them.*
2. What two things does carving a PNG look for?
   *The signature at the start and `IEND` plus its CRC at the end.*
3. Why search for `IEND` only after the signature?
   *An `IEND` earlier in the junk is not the end of this file.*
4. What do `skip` and `count` do in `dd`?
   *Where to start, and how many blocks (here bytes) to copy.*
5. Why check a carved file with `file`?
   *Parts of it may have been overwritten or scattered.*
