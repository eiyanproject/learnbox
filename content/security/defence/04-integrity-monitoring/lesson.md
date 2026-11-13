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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **foothold** | an attacker's first access to a system |
| **backdoor** | a hidden way back in, such as a changed login program that accepts a secret password |
| **web shell** | a small file dropped on a web server that lets an attacker run commands through it |
| **file integrity monitoring** (FIM) | recording a hash of every important file, and checking later whether any changed |
| **hash** (digest) | a fixed-size fingerprint of a file's contents (Foundations lesson 2) |
| **SHA-256** | the hash used here |
| **baseline** | the hashes taken while the system is known to be good |
| **known-good** (trusted) | a state you are confident has not been tampered with |
| **ground truth** | the reference everything else is compared with |
| **changed** | in both the baseline and now, with a different hash |
| **added** | present now, not in the baseline |
| **removed** | in the baseline, missing now |
| **Tripwire**, **AIDE** | well-known FIM tools for Linux |
| **tripwire** (idea) | an alarm that goes off when something is disturbed; it does not stop anyone |
| **after the fact** | it tells you a change happened; it does not prevent it |
| **read-only media** | storage that cannot be changed, such as a write-protected disk or a separate server |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `sha256sum file1 file2 > baseline.sha256` | records the hashes of those files in `baseline.sha256` |
| `sha256sum -c baseline.sha256` | rehashes each file and prints `OK` or `FAILED` |
| `sudo aide --init`, `sudo aide --check` | builds AIDE's baseline database; compares against it |
| `python fim.py` | runs your program: compares a baseline with a changed system |

### Python names

| Name | What it does |
|---|---|
| `{name: hashlib.sha256(data).hexdigest() for name, data in files.items()}` | a dict of each file name to its hash |
| `[n for n in base if n in current and base[n] != current[n]]` | names in both, with different hashes |
| `[n for n in current if n not in base]` | names that are new |
| `[n for n in base if n not in current]` | names that are gone |
| `sorted(list)` | the names in alphabetical order |

---

An intruder who gets a **foothold** changes things. They replace a system
program with a **backdoored** copy, edit a config to open a hole, or drop a
**web shell** on a web server. **File integrity monitoring** (FIM) catches all
of it in the same way: record a **hash** of every important file while the
system is known to be good, and compare against those hashes later. Any
change, however small, changes the hash.

## Baseline and compare

FIM works in two phases:

1. **Baseline**, on a trusted system: hash every file you care about, and
   store the hashes. This is your ground truth.
2. **Compare**, later and regularly: hash the files again and compare with the
   baseline.

Three kinds of change come out of the comparison:

| Kind | Meaning | Example |
|---|---|---|
| **changed** | the file is in both, with a different hash | `/bin/login` replaced with a backdoored copy |
| **added** | the file is new | `/var/www/upload/shell.php` |
| **removed** | the file has gone | a log file deleted to hide tracks |

`sha256sum` can do a tiny version of this by itself. Hash two files, change
one, and check:

```text
$ sha256sum sshd_config hosts > baseline.sha256
$ (someone changes PermitRootLogin to yes)
$ sha256sum -c baseline.sha256
sshd_config: FAILED
hosts: OK
sha256sum: WARNING: 1 computed checksum did NOT match
```

A changed hash on `/bin/login` is an alarm that needs no further explanation.
This is what the FIM tools **Tripwire** and **AIDE** do, for thousands of
files at once. It is also where Foundations lesson 2 pointed: a hash does not
keep a file secret, but it proves whether the file changed, and at scale that
proof is a security control.

## The honest limits

- FIM detects a change **after the fact**. It does not stop it.
- It only covers the files you put in the baseline.
- An attacker who can change the baseline as well can hide their changes.
  That is why the baseline is kept somewhere the attacker cannot reach: on
  another server, or on **read-only media**.

It is a tripwire, not a wall. But a tripwire on the right files turns a
silent compromise into a loud one.

## Your turn

In `fim.py`, files are a dict from name to `bytes`:

- `baseline(files)`: a dict from each name to its SHA-256 hex digest.
- `compare(base, current)`: given two such dicts, a dict with the keys
  `changed`, `added` and `removed`, each a sorted list of file names.

Run it:

```text
{'changed': ['/bin/login'], 'added': ['/tmp/shell'], 'removed': []}
```

## Check yourself

1. When must the baseline be taken?
   *While the system is known to be good.*
2. A file is in the baseline but missing now. Which kind of change?
   *Removed.*
3. Why does one changed byte always show up?
   *Any change to the contents changes the hash.*
4. Why keep the baseline away from the machine it describes?
   *An attacker who can edit it can hide their changes.*
5. Does FIM stop an attacker changing `/bin/login`?
   *No: it detects the change afterwards.*
