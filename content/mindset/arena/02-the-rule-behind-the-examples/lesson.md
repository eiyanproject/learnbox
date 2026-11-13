---
title: "Round 2: The rule behind the examples"
summary: Nobody wrote the specification down. There are only examples. Work out the rule and write it.
order: 2
files: [humanize.py]
run: python -i humanize.py
challenge:
  minutes: 15
  xp: 200
  requires:
    xp: 150
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **humanize** | turn a number into text a person reads easily, such as `"1h 2m 5s"` |
| **unit** | days, hours, minutes, seconds |
| **rule from examples** | the general behaviour the example table implies |
| **left out** | a unit with a value of 0 is not shown, except for `0` itself |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -i humanize.py` | runs the file, then leaves you at a Python prompt to try the functions |

### Python names

| Name | What it does |
|---|---|
| `divmod(a, b)` | the whole quotient and the remainder at once |
| `//`, `%` | whole-number division, remainder |
| `f"{n}d"` | an f-string: text with a value inside |
| `" ".join(parts)` | joins with spaces |
| `raise ValueError("...")` | the error for a negative number |

---

The person who knew how this was meant to work has left. What they left
behind is a table.

## The task

In `humanize.py`, write `humanize(seconds)`, which turns a number of seconds
into text. These are all the examples there are:

| `seconds` | Result |
|---|---|
| `0` | `"0s"` |
| `59` | `"59s"` |
| `60` | `"1m"` |
| `61` | `"1m 1s"` |
| `3600` | `"1h"` |
| `3725` | `"1h 2m 5s"` |
| `86400` | `"1d"` |
| `90000` | `"1d 1h"` |
| `172805` | `"2d 5s"` |

And one more thing they said in passing: a negative number is a mistake, and
should raise `ValueError`.

Before you type, say the rule to yourself in a sentence. What are the units?
When is a unit left out? What is special about `0`?
