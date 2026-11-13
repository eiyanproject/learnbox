---
title: "Round 1: Four bugs"
summary: Four short functions, one bug in each. Find the one wrong thing; do not rewrite.
order: 1
files: [report.py]
run: python -i report.py
challenge:
  minutes: 10
  xp: 150
  requires:
    xp: 50
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **bug report** | a user's description of what went wrong |
| **docstring** | the text under a `def` line saying what the function should do |
| **one bug** | each function has exactly one wrong thing; fix it, do not rewrite |
| **running total** | each value plus everything before it |
| **integer division** | dividing whole numbers and dropping the fraction, as `//` does |
| **first when tied** | among equally long words, the earliest one |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -i report.py` | runs the file, then leaves you at a Python prompt to try the functions |

### Python names

| Name | What it does |
|---|---|
| `len(values)` | how many items |
| `sum(values)` | their total |
| `text.split()` | splits text on whitespace |
| `/`, `//` | division / whole-number division |
| `>`, `>=` | greater than / greater than or equal |

### Errors

| Error | Means |
|---|---|
| `ZeroDivisionError` | dividing by zero, such as averaging an empty list |

---

`report.py` went out on Friday. Four bug reports came in over the weekend,
one for each function.

## The task

Each function in `report.py` has a docstring saying what it should do, and
**exactly one bug**. Fix all four.

The reports, as the users wrote them:

1. "`average([])` crashes instead of giving 0."
2. "`longest_word('one two six')` says `six`. It should say `one`: when
   several words are the longest, I want the first."
3. "`running_total([1, 2, 3])` gives `[2, 5]`. I expected `[1, 3, 6]`."
4. "`percent(1, 4)` gives `0.0`. A quarter is 25%."

Each fix is a small change to one line, or one line added. If you are
rewriting a whole function, read its report again.
