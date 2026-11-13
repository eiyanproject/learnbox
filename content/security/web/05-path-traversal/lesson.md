---
title: Path traversal
summary: Serving a file by the name the user asked for, until the name is ../../etc/passwd - and confining the path to its root.
order: 5
files: [files.py]
run: python files.py
hints:
  - "`traversal_payload`: a relative name using `../` to climb out of the web root. The test puts the secret one directory above the root, so one `../` reaches it."
  - "`serve_vulnerable` is provided and just joins the name onto the root, so `../` walks straight out."
  - "`serve_safe`: resolve the joined path with `os.path.realpath`, and serve it only if it is still inside `os.path.realpath(root)` - otherwise raise `ValueError`."
  - "Comparing resolved paths is the point: `..`, symlinks and absolute paths all collapse to a real location, and you check that location is under the root."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **path** | where a file is, as directory names joined with `/`: `/var/www/index.html` |
| **absolute path** | a path starting with `/`, counted from the very top of the file system |
| **relative path** | a path counted from some other directory: `images/logo.png` |
| **`..`** | "the parent directory": one level up |
| **`.`** | "this directory" |
| **web root** (base directory) | the one directory a web server is meant to serve files from |
| **path traversal** (directory traversal) | a file name that climbs out of the intended directory with `../` |
| **`/etc/passwd`** | the Linux file that lists user accounts; the classic proof that traversal worked |
| **symbolic link** (symlink) | a file that points to another path, like a shortcut |
| **resolve** (canonicalise) | work out the one true absolute path, with `..`, `.` and symlinks followed |
| **confine** | make sure the resolved path is still inside the root |
| **`os.sep`** | the character between directory names: `/` on Linux |
| **denylist** | a list of bad patterns to refuse, such as `..`; fragile, because attackers find other spellings |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `realpath path` | prints the resolved absolute path |
| `python files.py` | runs your program: prints your payload |

### Python names

| Name | What it does |
|---|---|
| `import os` | loads Python's operating-system helpers |
| `os.path.join(root, name)` | joins two parts of a path with `/`; if `name` is absolute, `root` is thrown away |
| `os.path.normpath(path)` | tidies a path, removing `..` and `.` by text alone (no symlinks) |
| `os.path.realpath(path)` | the resolved absolute path, with symlinks followed |
| `full.startswith(base + os.sep)` | `True` when `full` is somewhere inside the directory `base` |
| `open(path).read()` | the whole contents of a file, as text |
| `raise ValueError("...")` | stops with an error saying what was wrong |
| `serve_vulnerable(root, name)` | given to you: opens `root` joined with `name`, with **no** check |

---

A download page, a template loader, a file server: anywhere a site opens a
file whose **name came from the user**, there is a risk of **path traversal**.
If the name is joined onto a base directory and opened, a name like
`../../etc/passwd` climbs out of the intended folder and reads anything the
program is able to read.

## Paths in brief

A **path** says where a file is, as directory names joined by `/`. One that
starts with `/` is **absolute**: counted from the top of the file system. One
that does not is **relative**. Two special names appear inside paths:

- `.` means "this directory";
- `..` means "the parent directory", one level up.

So `/var/www/../secret.txt` is really `/var/secret.txt`: go into `www`, then
back up to `var`.

## The attack

A site keeps its files in a **web root**, say `/var/www`, and serves them by
name:

```python
def serve(root, name):
    return open(os.path.join(root, name)).read()
```

Nothing stops the name from containing `..`:

```pycon
>>> import os
>>> os.path.join("/var/www", "../../etc/passwd")
'/var/www/../../etc/passwd'
>>> os.path.normpath("/var/www/../../etc/passwd")    # what that path really means
'/etc/passwd'
>>> os.path.join("/var/www", "/etc/passwd")          # an absolute name drops the root
'/etc/passwd'
```

The first `..` climbs from `www` to `var`, the second from `var` to `/`, and
the path ends at `/etc/passwd`, the list of user accounts. The last line shows
a second trap: when the name is absolute, `os.path.join` throws the root away
entirely.

With the right number of `../`, an attacker can read the site's source code,
configuration files with database passwords, or SSH keys: whatever the web
server's account can read. You will write the name that escapes the web root.

## The defence: resolve, then check

Never trust that a joined path stays where you put it. **Resolve** it to its
real location, then **check** that the location is still inside the root:

```python
base = os.path.realpath(root)
full = os.path.realpath(os.path.join(root, name))
if full != base and not full.startswith(base + os.sep):
    raise ValueError("outside the web root")
return open(full).read()
```

1. `os.path.realpath` gives the true absolute path: `..` and `.` removed,
   symlinks followed.
2. Do it for both the root and the requested file.
3. The file is allowed only if its real path starts with the root's real path
   followed by `/`. The `+ os.sep` matters: without it, `/var/www-private`
   would count as "inside" `/var/www`.

Resolving **before** checking is the essential part. Searching the raw name
for `..` by hand (a **denylist**) is the fragile non-fix: it misses absolute
paths, symlinks inside the root that point outside, and encodings that only
turn into `..` later. Let the operating system work out the real path, then
check that.

The theme from the injection lessons holds: do not try to spot the dangerous
string; take away its power. Here, that means turning it into a real location
you can test.

## Your turn

`serve_vulnerable(root, name)` is given to you. In `files.py`:

- `traversal_payload()`: a `name` that escapes the web root to read
  `secret.txt`, a file one directory **above** the root. (The checks create
  both the root and the file.)
- `serve_safe(root, name)`: serve the file only when it resolves to a
  location inside `root`; raise `ValueError` otherwise.

## Check yourself

1. What is `/var/www/images/../../secret.txt`, resolved?
   *`/var/secret.txt`.*
2. What does `os.path.join("/var/www", "/etc/passwd")` return?
   *`'/etc/passwd'`: an absolute name drops the root.*
3. Why not just refuse any name that contains `..`?
   *It misses absolute paths, symlinks and other spellings.*
4. Why check against `base + os.sep` rather than `base`?
   *So that a sibling like `/var/www-private` does not count as inside.*
5. What does `os.path.realpath` do that `os.path.normpath` does not?
   *It follows symlinks to the true location.*
