---
title: Knowing when to stop
summary: The difference between unfinished and imperfect, why the third abstraction is the right one to build, and what to do with code you might need later.
order: 2
files: [enough.py]
run: python -i enough.py
hints:
  - "`apply_discount` handles exactly the two cases asked for. Do not add a plugin system, a registry or a strategy pattern - the test checks the simple shape."
  - "`parse_config` should accept the documented keys and IGNORE unknown ones rather than crashing - forgiving input, strict output."
  - "`retry` takes a function and attempts; return the first success, and raise the last exception if all attempts fail."
  - "`delete_old_entries` should delete, not comment out - the test checks that removed entries are actually gone."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **unfinished** | a real case missing: must be fixed |
| **imperfect** | working but not elegant: the normal state |
| **generalise** | build an abstraction to cover many cases |
| **axis of variation** | the way cases really differ; two examples do not show it |
| **wrong abstraction** | a general design that later cases fight against |
| **duplication** | the same code twice; cheaper than the wrong abstraction |
| **plugin system** | machinery for adding cases nobody has asked for |
| **liberal in what you accept** | ignore unknown input, validate what you know, produce predictable output |
| **breaking change** | a change that makes old input or callers fail |
| **dead code** | commented-out or unreachable code; delete it |
| **version control** | Git: keeps old code, so you need not |
| **paged at 3am** | woken to fix production; the real test of good enough |
| **retry** | try again; re-raise the last error if all attempts fail |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -i enough.py` | runs the file, then leaves you at a Python prompt to try the functions |

### Python names

| Name | What it does |
|---|---|
| `text.splitlines()` | the lines of the text |
| `line.strip()`, `line.startswith("#")` | trims / tests for a comment |
| `key, value = line.split("=", 1)` | splits at the first `=` |
| `int(value)`, `value.lower() == "true"` | the port number / the debug flag |
| `for _ in range(attempts):` | repeat a number of times |
| `try: return func() except Exception as e: last = e` | keep the last error |
| `raise last` | re-raises it |
| `raise ValueError(...)` | for an unknown discount kind |

---

Two opposite failures. **Unfinished** is missing a case that exists — a
boundary unhandled, an error unreported. **Imperfect** is a working solution
that is not elegant. The first must be fixed. The second is the normal state of
working software.

Knowing which one you are looking at is a real skill, and getting it wrong is
expensive in both directions.

## Build the third one

The temptation is to generalise at the second case. But two examples do not
show you the axis of variation; they show you one difference, which is often
the wrong one. An abstraction built from two cases usually has to be
dismantled at the third.

Waiting costs a little duplication. Guessing wrong costs a framework everyone
has to work around. Duplication is cheaper than the wrong abstraction — it is
local, visible, and easy to remove later.

## Be liberal in what you accept

A config parser that crashes on an unknown key makes every future addition a
breaking change. Ignore what you do not recognise, validate what you do, and be
strict about what you *produce*. Forgiving input, predictable output.

## Delete the dead code

Commented-out code is worse than no code. It is not executed, not tested, not
maintained, and the reader cannot tell whether it matters. Version control has
it. Delete it.

The same for the `if False:` branch, the unused parameter kept "just in case",
and the function nothing calls. Each one is a question every future reader has
to answer and cannot.

## When to stop

Stop when it handles the cases that exist, fails clearly on those it does not,
and a reader can follow it. Not when it is beautiful, and not when it could
handle cases nobody has.

The remaining question is whether you would be comfortable being paged about
this code at 3am. That is a much better test than whether it is elegant.

## Your turn

`enough.py` is over-engineered and under-finished at once. Rewrite it as:

- `apply_discount(price, kind)` — `"none"`, `"half"` or `"ten"`, raising
  `ValueError` for anything else. Two cases, no plugin system.
- `parse_config(text)` — `key=value` lines into a dict, ignoring blank lines,
  `#` comments and unknown keys (the known ones are `host`, `port`, `debug`),
  with `port` an int and `debug` a bool
- `retry(func, attempts)` — return the first success; re-raise the last
  exception if none succeed
