---
title: Hello, Python
summary: Run your first program, meet print(), and learn how this page works.
order: 1
files: [hello.py]
run: python hello.py
hints:
  - "Each `print()` call writes one line. Two lines of output need two calls, one under the other."
  - "The text must match exactly, including the capital letters, the comma and the full stop (period) at the end: `print(\"Hello, learnbox!\")`"
---

A Python program is a plain text file, usually ending in `.py`. Each line of
it is an instruction, called a **statement**. When you run the file, Python
reads it from the top and carries out the statements one at a time, in order,
until it reaches the bottom.

If you have used a language such as C or Java, two things are missing here.
There is no `main` function you have to write before anything happens, and
there is no separate compile step that turns your code into a program first.
You save the file and run it, and that is all.

## How this page works

The editor on the right is not a copy or a simulation. It shows a real file
that lives in your home folder on the server. Everything you type is saved
to that file automatically, so there is no Save button to remember.

Below the editor is a real terminal: a `bash` shell, the same kind you would
get on any Linux machine. It starts in the same folder as the file, so these
two things are the same file seen in two places:

- the `hello.py` tab in the editor
- the `hello.py` that is listed when you type `ls` (list files) in the terminal

Three buttons do the rest:

- **Run** types this lesson's run command into the terminal for you, here
  `python hello.py`, and presses Enter. You could type it yourself and get
  exactly the same result.
- **Check** runs hidden tests against your code and shows which ones pass.
  The tests are small programs that run your code and compare what it does
  with what the lesson asked for.
- **Reset** puts the starter files back, for when you want to start the
  exercise over. Your old files are not thrown away: they are kept in
  `~/learn/.reset-backups` (`~` is short for your home folder).

You can also edit files with a terminal editor such as `nano` or `vim`. The
editor on the page notices when a file changes on disk and reloads it, so the
two never disagree.

## print()

`print()` is a **function**: a named piece of code that does a job when you
**call** it. You call a function by writing its name followed by brackets,
and whatever you put inside the brackets is handed to it. `print()` writes
what it is given to the terminal, followed by a line break:

```python
print("Hello")
print("Two", "words")   # several values are joined with a space
print()                  # an empty line
```

```output
Hello
Two words

```

Each call ends its line, so the next call starts on a new one. That is why
two lines of output take two `print()` calls.

Text in quotes is a **string**: Python's word for a piece of text. The quotes
mark where the text starts and stops; they are not part of the text, and
`print()` does not show them. Single and double quotes mean the same thing,
so `'hi'` and `"hi"` are identical. Pick one and close the string with the
same kind you opened it with.

The quotes matter. Without them, Python reads the word as the name of
something in your program rather than as text, and stops with an error
because nothing by that name exists:

```pycon
>>> print(Hello)
Traceback (most recent call last):
  ...
NameError: name 'Hello' is not defined
```

Anything after a `#` on a line is a **comment**: a note for people reading
the code. Python ignores it completely, so you can write whatever you like
there.

## When something goes wrong

Mistakes are normal, and Python tells you about them. When it cannot run a
line it prints a **traceback**: a few lines of report ending with the kind of
error and a short message. Read the last line first; it says what went wrong.
The lines above it say where, including the file name and line number.

The two errors you will meet most often at the start are:

- `SyntaxError`: the code is not valid Python at all, for example a missing
  closing quote or bracket. Python notices this before running anything.
- `NameError`: you used a name Python does not know, often a typo such as
  `prnt("hi")`, or text that is missing its quotes.

Fix the line it points at, save (automatic here), and run again.

## The interactive prompt

You do not always need a file. Type `python` in the terminal and press
Enter, and you get a `>>>` prompt instead. Each line you type there runs as
soon as you press Enter, and if it produces a value, Python shows the value
straight away without you having to `print()` it:

```pycon
>>> 2 + 3
5
>>> print("hi")
hi
```

In this lesson, lines that start with `>>>` are what you type, and the lines
under them are what Python answers. Do not type the `>>>` itself.

The prompt is the fastest way to try a small idea or check how something
behaves. Nothing you type there is saved, though, so real programs go in a
file. Leave the prompt with `exit()` or Ctrl+D, which brings you back to the
normal terminal.

## Your turn

Make `hello.py` print exactly these two lines:

```text
Hello, learnbox!
Python is running.
```

The tests compare your output with these lines character for character, so
capital letters, spaces and punctuation all count. Press **Run** to see the
output, then **Check** when it looks right.
