---
title: File integrity monitoring
summary: An attacker who gets in changes files - a backdoored binary, an edited config. A baseline of hashes makes every change visible.
order: 4
files: [fim.py]
run: python fim.py
hints:
  - "`baseline`: hash every file's contents with SHA-256 and return a dict of name to hex digest."
  - "`compare`: a file is 'changed' if it is in both but its hash differs, 'added' if only in current, 'removed' if only in the baseline."
  - "Return a dict with sorted lists under the keys 'changed', 'added' and 'removed'."
  - "The hash is the whole idea: you cannot watch every byte of every file, but you can watch one digest per file and know instantly when one moves."
---

An intruder who gains a foothold changes things: replaces a system binary with a
backdoored copy, edits a config to open a hole, drops a web shell. **File
integrity monitoring** (FIM) catches all of it the same way - by recording a
**hash** of every file when the system is known-good, and comparing against it
later. Any change, however small, moves the hash.

## Baseline and compare

Two phases:

1. **Baseline**, on a trusted system: hash every file you care about and store
   the digests. This is ground truth.
2. **Compare**, later: hash the files again and diff against the baseline. Three
   kinds of change fall out - files whose hash **changed**, files **added** that
   were not there before, and files **removed**.

A changed hash on `/bin/login` is an alarm that needs no further explanation.
This is what Tripwire and AIDE do, and what the integrity lesson from
foundations pointed toward: a hash does not keep a file secret, but it proves
whether it changed - and at scale, that proof is a security control.

## The honest limits

FIM detects change after the fact, and only for files you baselined; an attacker
who alters the baseline itself defeats it, which is why the baseline is kept
somewhere the attacker cannot reach. It is a tripwire, not a wall - but a
tripwire on the right files turns a silent compromise into a loud one.

## Your turn

In `fim.py` (files are a dict of name to `bytes`):

- `baseline(files)` - a dict of name to SHA-256 hex digest
- `compare(base, current)` - a dict with `changed`, `added` and `removed`, each
  a sorted list of file names
