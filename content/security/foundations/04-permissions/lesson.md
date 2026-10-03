---
title: File permissions and least privilege
summary: Reading and writing Unix mode bits, spotting a file that gives away too much, and the principle that decides how tight is tight enough.
order: 4
files: [perms.py]
run: python perms.py
hints:
  - "`mode_to_rwx`: for each of the three groups (owner, group, other) pull its 3 bits out of the octal number and map 4/2/1 to r/w/x. Owner bits are `(mode >> 6) & 7`, group `(mode >> 3) & 7`, other `mode & 7`."
  - "`is_world_writable`: the 'write' bit for 'other' is octal 002, so test `mode & 0o002`."
  - "`is_too_open_for_secret`: a secret should be readable only by its owner, so any group or other bit set is too open - test `mode & 0o077`."
  - "`tighten`: keep only the owner bits - `mode & 0o700`."
---

Every file on a Unix system carries **permission bits** saying who may read,
write and execute it. Get them wrong and a secret is world-readable or a script
is world-writable - two of the most common real misconfigurations there are,
and both are found by simply looking at the mode.

## The bits

Permissions come in three groups of three: **owner**, **group**, **other**
(everyone else). Each group has read (`r`), write (`w`) and execute (`x`). The
familiar `rw-r--r--` from `ls -l` is those nine bits written out.

They are also written as an **octal** number, because each group of three bits
is exactly one octal digit:

| | r | w | x | |
|---|---|---|---|---|
| value | 4 | 2 | 1 | add them up |

So `rw-r--r--` is `6 4 4` = `0o644`: owner read+write (4+2), group read (4),
other read (4). `rwxr-x---` is `750`. A private key must be `600` - owner only -
and `ssh` refuses to use one that is looser, because a key others can read is
already compromised.

## Least privilege

The principle that governs all of this: **grant the minimum access needed, and
no more.** A config file with a password in it should be readable by the one
account that needs it and nobody else. A log directory the web server writes to
should not be writable by every user on the box. Every bit you grant beyond the
minimum is a door you have to trust everyone not to walk through.

"Too open" is not about a single magic number - it depends on what the file is.
A secret's bar is the strictest: owner-only. The attack is to go looking for
files whose mode is looser than their contents deserve; the defence is to set
the mode to the minimum and check it stays there.

## Your turn

In `perms.py` (mode values are integers, written in octal like `0o640`):

- `mode_to_rwx(mode)` - the nine-character string, e.g. `0o640` gives
  `"rw-r-----"`
- `is_world_writable(mode)` - `True` when anyone on the system can write the file
- `is_too_open_for_secret(mode)` - `True` when anyone other than the owner has
  any permission on it at all (read, write or execute)
- `tighten(mode)` - the same file restricted to owner-only access
