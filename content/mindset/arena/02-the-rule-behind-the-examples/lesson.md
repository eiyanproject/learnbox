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
