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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **baseline** | the hashes of every file, taken while the system was known to be good (Defence lesson 4) |
| **known-good** | a state you trust has not been tampered with |
| **tampered** (swapped) file | one whose contents were changed or replaced |
| **file integrity monitoring** | comparing current hashes with the baseline to find changes |
| **SHA-256** | the hash used to fingerprint each file |
| **artifact** | one piece of evidence worth examining, such as a changed file |
| **PNG** | an image format built from chunks (Forensics lesson 3) |
| **IEND** | the chunk that officially ends a PNG; it is followed by a 4-byte CRC |
| **trailing data** | bytes after IEND and its CRC; image viewers ignore them (Forensics lesson 4) |
| **payload** | here, the hidden data the replacement file carries |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `sha256sum -c baseline.sha256` | the shell version of step 1: which files no longer match |
| `python tamper.py` | runs your program: names the changed file and prints what it hides |

### Python names

| Name | What it does |
|---|---|
| `ORIGINAL`, `CURRENT` | given to you in `data.py`: dicts of file name to bytes, before and now |
| `hashlib.sha256(data).hexdigest()` | a file's hash as hex |
| `for name, data in current.items():` | each current file with its name |
| `name in original` | the file existed in the baseline |
| `data.find(b"IEND")` | where `IEND` starts, or `-1` |
| `data[marker + 4 + 4:]` | everything after `IEND` and its CRC |

---

A system was **baselined** while it was known to be good: every file was
hashed. Later, one file is different. This challenge is file integrity
monitoring meeting forensics. The hash tells you **which** file was touched;
then you recover what the replacement is carrying.

## The brief

`ORIGINAL` and `CURRENT` in `data.py` are dicts from file name to bytes: the
baseline state and the current state. Exactly one file's contents changed.
The replacement looks like a normal image, but has a secret appended after
the PNG's official end (its IEND chunk), where an image viewer never looks.

There are two steps:

1. **Find the changed file** by comparing hashes (Defence lesson 4).
2. **Extract the hidden trailing data** from it (Forensics lesson 4).

This is the real order of a compromise investigation. Integrity monitoring
tells you **that** something changed and **which** file. Only then does
forensics tell you **what** the change was. The hash narrows a whole file
system down to the one **artifact** worth taking apart, which is what makes
the second step practical at all.

## Your turn

In `tamper.py`:

- `find_tampered(original, current)`: the name of the file whose contents
  changed, or `None` if none did.
- `extract_payload(data)`: the bytes hidden after the PNG's IEND chunk and its
  CRC, or `b""` if there are none.

## Check yourself

1. Why compare hashes rather than look at every file's contents?
   *One hash per file shows at once which one changed.*
2. Where does a PNG officially end?
   *After the IEND chunk and its 4-byte CRC.*
3. Why does an image viewer not show the hidden data?
   *It stops reading at IEND.*
