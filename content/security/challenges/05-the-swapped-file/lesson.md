---
title: "Challenge: the swapped file"
summary: One file changed since the known-good baseline. Find it, and recover what the replacement is hiding.
order: 5
files: [tamper.py]
run: python tamper.py
hints:
  - "Compare SHA-256 of each current file against the baseline hash; the one that differs is the swap."
  - "The replacement is a PNG with data appended after its IEND chunk - the trailing-data trick from the forensics section. Return the bytes after IEND plus its 4-byte CRC."
---

A system was baselined when it was known-good, and its files were hashed. Later,
one file is different. This is file integrity monitoring meeting forensics: the
hash tells you *which* file was touched, and then you recover what the
replacement is carrying.

## The brief

`ORIGINAL` and `CURRENT` in `data.py` are dicts of filename to bytes - the
baseline and the current state. Exactly one file's contents changed. The
replacement looks like a normal image but has a secret appended after the PNG's
official end (its IEND chunk), invisible to an image viewer.

Two steps: find the changed file by comparing hashes, then extract the hidden
trailing data from it. This is the real order of a compromise investigation -
integrity monitoring tells you *that* something changed and *which* file, and
only then does forensics tell you *what* the change was. The hash narrows a
whole filesystem down to the one artifact worth pulling apart, which is what
makes the recovery step tractable at all.

## Your turn

In `tamper.py`:

- `find_tampered(original, current)` - the name of the file whose contents
  changed
- `extract_payload(data)` - the bytes hidden after the PNG's IEND chunk
