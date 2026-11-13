---
title: Hypotheses and bisection
summary: Halving the search space instead of reading everything, and testing one belief at a time so a passing test means something.
order: 2
files: [bisect_bug.py]
run: python -i bisect_bug.py
hints:
  - "`parse_row` is where the bug is - the other functions are fine. Read them to confirm that, which is itself the lesson."
  - "The header row should be skipped by `load`, not by `parse_row` - each function keeps one job."
  - "A price like '1.5' must become a float, and a quantity like '2' an int. Row values arrive as strings, always."
  - "`summarise` should ignore rows that fail to parse rather than crashing the whole import - return the ones that worked."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **bisect** | check the middle, and throw away the half that is fine |
| **pipeline** | steps where each passes its result to the next |
| **`git bisect`** | the same search over commits |
| **hypothesis** | a sentence that can be wrong, with a check to test it |
| **reproduce** | make the bug happen on purpose, as small as possible |
| **stale build** | running old compiled code, not what you are reading |
| **cached value** | a stored old answer used instead of a fresh one |
| **swallowed exception** | an error caught and hidden |
| **header** | the first row of a CSV, naming the columns |
| **malformed row** | one that does not parse |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -i bisect_bug.py` | runs the file, then leaves you at a Python prompt to try the functions |

### Python names

| Name | What it does |
|---|---|
| `print(type(x), repr(x))` | shows exactly what a value is |
| `repr(x)` | shows `"2"` against `2`, and trailing spaces |
| `rows[1:]` | everything after the header |
| `name, qty, price = row` | unpacks a row; fails if it has the wrong length |
| `int(qty)`, `float(price)` | parse numbers |
| `try: ... except ValueError: continue` | skips a row that fails |

---

Debugging is a search. The only question that matters is how fast you shrink
the space.

## Bisect, do not read

Given a pipeline of six steps and a wrong answer at the end, do not start at
step one. Check the value at step three. Whichever half it is in, you have
eliminated the other — and three or four checks of that kind isolate a bug in a
system you have never seen.

The same idea is `git bisect` for "it worked last month", and commenting out
half a config file. It is one technique wearing different clothes.

## One hypothesis at a time

A hypothesis is a sentence that can be wrong:

> The quantity is arriving as a string, so the multiplication concatenates.

Now design the smallest check that distinguishes it — print the type, or call
the function with a known input. If you change three things and it starts
working, you have learned nothing and probably introduced something.

## Trust nothing, verify cheaply

The bug is in the part you are certain about. That is not mysticism: the parts
you are unsure of get checked, so what survives is the assumption you never
tested.

Cheap verification beats careful reasoning. `print(type(x), repr(x))` at the
boundary takes four seconds and settles what ten minutes of reading might not.
Use `repr`, not `str` — it is how you find the trailing space and `"2"` against
`2`.

## Reproduce it smaller

A bug that needs the whole program to appear is hard to study. Shrink it: one
row instead of ten thousand, one function instead of the pipeline. Usually the
smaller reproduction *is* the diagnosis — you remove a part and the bug goes
with it.

## When it makes no sense

You are debugging something other than what you think. Wrong file, stale
build, a cached value, an exception being swallowed. Check that the code you
are reading is the code that runs — add a deliberate syntax error and confirm
it breaks.

## Your turn

`bisect_bug.py` has a small CSV-ish import pipeline. `summarise` gives wrong
answers. Find which stage is at fault and fix it.

- `parse_row(row)` — `["apple", "2", "1.5"]` becomes
  `("apple", 2, 1.5)`, raising `ValueError` for a malformed row
- `load(rows)` — skips the header, returns the parsed rows, ignoring any that
  fail to parse
- `summarise(rows)` — `{"items": <count>, "total": <sum of qty * price>}`
