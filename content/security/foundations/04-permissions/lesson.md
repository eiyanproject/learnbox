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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **permission bits** (mode) | nine yes/no settings on every file saying who may read, write and execute it |
| **owner** | the user the file belongs to |
| **group** | a named set of users that the file also belongs to |
| **other** ("world") | every user who is neither the owner nor in the group |
| **read** (`r`) | may see the contents; for a directory, may list its names |
| **write** (`w`) | may change the contents; for a directory, may create, rename and delete files in it |
| **execute** (`x`) | may run the file as a program; for a directory, may enter it |
| **octal** | base 8, digits 0 to 7; one octal digit is exactly three bits, so one digit per group |
| **`0o640`** | how Python writes the octal number 640; the shell commands write just `640` |
| **world-readable** | anyone on the machine can read it |
| **world-writable** | anyone on the machine can change or replace it |
| **misconfiguration** | a setting that is wrong, as opposed to a bug in the code |
| **least privilege** | give each user and program the minimum access it needs, and nothing more |
| **private key** | the secret half of a key pair, as used by SSH; it must be readable by its owner only |
| **bit mask** | a number used to pick out or clear certain bits of another |
| **shift** (`>>`) | moving bits to the right; `>> 6` moves the owner's three bits to the bottom |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `ls -l` | lists files with their mode, owner, group, size and date |
| `ls -ld dir` | the same for a directory itself, not its contents |
| `stat -c '%A %a %n' file` | the mode as letters (`%A`), as octal (`%a`), then the name (`%n`) |
| `chmod 600 file` | sets the mode to `600`: owner read and write, nobody else anything |
| `chmod o-w file` | removes write (`-w`) from other (`o`); `u`, `g`, `o` are owner, group, other |
| `find / -perm -0002 -type f` | finds world-writable files: any file with the "other write" bit set |
| `python perms.py` | runs your program, printing four modes |

### Python names

| Name | What it does |
|---|---|
| `0o644` | an integer written in octal |
| `f"{m:04o}"` | a number printed as four octal digits, `0644` |
| `mode >> 6` | the mode shifted right by six bits, leaving the owner's bits at the bottom |
| `& 7` | keeps only the lowest three bits (7 is binary `111`) |
| `bits & 4` | non-zero when the read bit is set (4 is binary `100`) |
| `mode & 0o002` | non-zero when "other" may write |
| `mode & 0o077` | non-zero when the group or other has any permission |
| `mode & 0o700` | the mode with everything except the owner's bits cleared |
| `bool(x)` | `False` for 0, `True` for anything else |
| `for shift in (6, 3, 0):` | owner, then group, then other |
| `"".join(out)` | the list of characters joined into one string |

---

Every file on a Linux or other Unix system carries **permission bits**
saying who may read, write and run it. Getting them wrong is one of the most
common real misconfigurations: a secret that every user can read, or a
script that every user can change. Both are found by simply looking.

## Reading the bits

There are three groups of users:

- **owner**: the user the file belongs to;
- **group**: the members of the file's group;
- **other**: everyone else on the machine.

Each group has three permissions: **read** (`r`), **write** (`w`) and
**execute** (`x`). `ls -l` shows the nine bits as letters, with `-` for "no"
(your user name in place of `alice`):

```text
$ ls -l
-rw------- 1 alice alice 2 Nov 13 23:46 id_ed25519
-rw-r--r-- 1 alice alice 2 Nov 13 23:46 notes.txt
```

Read the first column in pieces: the first character is the type (`-` a
file, `d` a directory), then three letters for the owner, three for the
group, three for other. So `notes.txt` is `rw-` `r--` `r--`: the owner may
read and write, the group and everyone else may only read.

### The same bits as a number

Each group of three bits is exactly one **octal** digit, so the whole mode is
written as three digits. Inside a digit, each permission has a value, and you
add them up:

| r | w | x |
|---|---|---|
| 4 | 2 | 1 |

- `rw-` is 4 + 2 = **6**; `r--` is **4**; `---` is **0**; `rwx` is **7**.
- So `rw-r--r--` is **644**, and `rwxr-x---` is **750**.

`stat` shows both forms side by side:

```text
$ stat -c '%A %a %n' *
-rw------- 600 id_ed25519
-rw-r--r-- 644 notes.txt
```

A private SSH key must be **600**, owner only. `ssh` refuses to use a key
that others can read, because a key that others can read is already leaked.
`chmod 600 file` sets that mode.

### Doing it in code

In Python an octal number is written `0o644`. To get one group's three bits,
shift them to the bottom and keep only those: `(mode >> 6) & 7` is the owner,
`(mode >> 3) & 7` the group, `mode & 7` other. Then test each bit: `& 4` for
read, `& 2` for write, `& 1` for execute.

A single test can check one permission across the whole mode. "Other may
write" is the bit `0o002`, so `mode & 0o002` is non-zero exactly when a file
is **world-writable**. `0o077` covers every group and other bit at once.

```pycon
>>> from perms import mode_to_rwx, tighten
>>> mode_to_rwx(0o640)
'rw-r-----'
>>> oct(tighten(0o755))
'0o700'
```

## Least privilege

The principle behind all of this: **give the minimum access needed, and no
more.** A configuration file with a database password in it should be
readable by the one account that needs it and nobody else. A log directory
that the web server writes to should not be writable by every user. Every
bit beyond the minimum is a door you have to trust everyone not to walk
through.

"Too open" is not one magic number; it depends on what the file is:

| File | Sensible mode | Why |
|---|---|---|
| a private key, a password file | `600` | owner only |
| a script the owner runs | `700` or `750` | others need not change it, and often not run it |
| a public web page | `644` | everyone may read; only the owner writes |
| anything | never world-writable (`o+w`) | anyone could replace it |

An attacker who gets onto a machine as an ordinary user looks for exactly
these mistakes, for example with `find / -perm -0002 -type f` for
world-writable files. The defence is to set the minimum mode and check that
it stays that way.

## Your turn

In `perms.py` (modes are integers, written in octal like `0o640`):

- `mode_to_rwx(mode)`: the nine-character string, so `0o640` gives
  `"rw-r-----"`.
- `is_world_writable(mode)`: `True` when anyone on the system can write the
  file.
- `is_too_open_for_secret(mode)`: `True` when anyone other than the owner
  has any permission at all (read, write or execute).
- `tighten(mode)`: the same mode restricted to owner-only access.

Run it:

```text
0644  rw-r--r--  secret_leak=True
0600  rw-------  secret_leak=False
0777  rwxrwxrwx  secret_leak=True
0640  rw-r-----  secret_leak=True
```

## Check yourself

1. What is `rwxr-x---` in octal?
   *750: 4+2+1, 4+1, 0.*
2. What does the octal digit `6` mean?
   *Read and write, not execute.*
3. Why does `ssh` refuse a private key with mode `644`?
   *Other users can read it, so it may already be stolen.*
4. Which bit makes a file world-writable?
   *`0o002`, write for other.*
5. A config file holds a password and is `640`. Too open?
   *For a secret, yes: the group can read it. `600` is the bar.*
