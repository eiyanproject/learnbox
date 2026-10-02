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

A download endpoint, a template loader, a file server - anywhere a site opens a
file whose name came from the user - risks **path traversal**. If the name is
joined onto a base directory and opened, a name like `../../../../etc/passwd`
walks out of the intended folder and reads anything the process can.

## The attack

```python
def serve(root, name):
    return open(os.path.join(root, name)).read()
```

`os.path.join("/var/www", "../../etc/passwd")` is `/var/www/../../etc/passwd`,
which resolves to `/etc/passwd`. The `..` entries mean "parent directory", and
nothing here stops the name from climbing above `root`. Source code, config
files with credentials, SSH keys - all readable with the right number of `../`.
You will write the payload that escapes the web root.

## The defence

Never trust that a joined path stays where you put it - **resolve it and check**.
`os.path.realpath` collapses `..`, follows symlinks and returns the true
absolute location. Confirm that location is still inside the root before opening:

```python
base = os.path.realpath(root)
full = os.path.realpath(os.path.join(root, name))
if full != base and not full.startswith(base + os.sep):
    raise ValueError("outside the web root")
return open(full).read()
```

Resolving *before* checking is essential: inspecting the raw name for `..` by
hand is the fragile non-fix, defeated by tricks like `....//` or an absolute
path or a symlink. Let the operating system compute the real path, then verify
it is confined. The theme holds from the injection lessons: do not reason about
the dangerous string, remove its power - here by reducing it to a real location
you can test.

## Your turn

`serve_vulnerable(root, name)` is provided. In `files.py`:

- `traversal_payload()` - a `name` that escapes the web root to read a file one
  directory above it
- `serve_safe(root, name)` - serve the file only when it resolves to a location
  inside `root`; raise `ValueError` otherwise
