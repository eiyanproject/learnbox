---
title: Recognising a dangerous pattern
summary: Some library calls are vulnerabilities almost by definition. Spotting them - and naming the safe replacement - is the heart of a code or binary review.
order: 4
files: [review.py]
run: python review.py
hints:
  - "`dangerous_calls`: for each called function that appears in `DANGERS`, record its reason. Return a dict of name to reason."
  - "`safer_alternative`: look the name up in `SAFER`; return the replacement, or None if it is not a known dangerous call."
  - "`review`: a function is risky if it calls any dangerous function. Return the set of function names that do."
  - "The judgement is always the same: does this call let input decide something it should not - a size, a format, a command?"
---

Some functions are dangerous almost wherever they appear, because their design
makes a mistake the default. Recognising them on sight - in source, or in the
import list of a binary - is the fastest, highest-value review there is, and it
is exactly what the `gets`/`system`/`strcpy` imports from the symbol lesson were
pointing at.

## The usual suspects

| Call | Why it is dangerous | Safe replacement |
|---|---|---|
| `gets` | no limit at all on what it reads - guaranteed overflow | `fgets` |
| `strcpy` / `strcat` | copy until a null, with no idea of the buffer size | `snprintf` (or `strlcpy` / `strlcat`) |
| `sprintf` | formats into a buffer with no size bound | `snprintf` |
| `system` | hands a string to the shell - the command injection lesson | `execve` with an argument list |
| `scanf("%s")` | reads an unbounded string into a fixed buffer | a width, `%9s` |

**A warning about the obvious replacement.** `strncpy` looks like the bounded
version of `strcpy` and is not a safe one. When the source is at least as long as
the limit, it copies exactly that many bytes and **does not write a null
terminator** - so the next read runs off the end of the buffer into whatever sits
beside it. `strncat`'s size argument means the space *remaining*, not the buffer
size, which is a different off-by-one trap. `snprintf` always terminates and
always respects the size you pass; `strlcpy`/`strlcat` do the same and are now
in glibc.

The thread tying them together is the one from the web section: a call where
**input decides a size, a format, or a command** that the programmer assumed
was fixed. `gets` lets input decide how many bytes to write; `system` lets input
decide what command to run.

## Review as a habit

A real review - of source or of a binary's imports - is largely this: scan for
the known-dangerous calls, and for each ask whether untrusted input reaches it.
Naming the safe replacement is half the job, because "don't use `gets`" is only
useful next to "use `fgets` with a size". This is defensive work - you are
finding the hole so it can be closed.

## Your turn

`DANGERS` (name to reason) and `SAFER` (name to replacement) are provided. In
`review.py`:

- `dangerous_calls(called)` - a dict of each dangerous call in `called` to its
  reason
- `safer_alternative(name)` - the safe replacement for a dangerous call, or
  `None`
- `review(functions)` - given `{function_name: [calls it makes]}`, the set of
  function names that make at least one dangerous call
