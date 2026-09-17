---
title: Hello, Python
summary: Run your first program, meet print(), and learn how this page works.
order: 1
files: [hello.py]
run: python hello.py
hints:
  - "`print()` puts each call on its own line. You need two calls."
  - "The text must match exactly, including the comma and the full stop: `print(\"Hello, learnbox!\")`"
---

Python runs a file from top to bottom, one statement at a time. There is no
`main` function to write and nothing to compile: you save the file and run it.

## How this page works

The editor on the right is a real file in your home directory on the server.
Everything you type is saved automatically. Below it is a real terminal: a
`bash` shell sitting in the same folder, so these two things are the same file:

- the `hello.py` tab in the editor
- `hello.py` when you type `ls` in the terminal

Three buttons do the rest:

- **Run** types the run command into the terminal for you (`python hello.py`).
- **Check** runs hidden tests against your code and shows which ones pass.
- **Reset** puts the starter files back (your old files are kept in `~/learn/.reset-backups`).

You can also edit with `nano` or `vim` in the terminal. The editor notices
when a file changes on disk and reloads it.

## print()

`print()` writes a line of text to the terminal:

```python
print("Hello")
print("Two", "words")   # several values are joined with a space
print()                  # an empty line
```

Text in quotes is a **string**. Single and double quotes mean the same thing:
`'hi'` and `"hi"` are identical.

Anything after `#` is a **comment**: Python ignores it.

## The interactive prompt

Type `python` in the terminal and press Enter. You get a `>>>` prompt where
each line runs as soon as you press Enter:

```pycon
>>> 2 + 3
5
>>> print("hi")
hi
```

That is the fastest way to try a small idea. Leave it with `exit()` or
Ctrl+D.

## Your turn

Make `hello.py` print exactly these two lines:

```text
Hello, learnbox!
Python is running.
```

Press **Run** to see the output, then **Check** when it looks right.
