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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **buffer** | a fixed-size area of memory that holds data, such as `char name[16]` |
| **buffer overflow** | writing past the end of a buffer, over whatever is stored next to it |
| **null terminator** (`\0`) | the zero byte that marks the end of a C string |
| **bounded** | told the size of the destination, and never writes beyond it |
| **unbounded** | writes as much as the input contains |
| **untrusted input** | anything that came from a user, a file or the network |
| **code review** | reading code to find bugs before they ship |
| **safe replacement** | the function to use instead, with the size made explicit |
| **off-by-one** | a mistake of exactly one, such as forgetting room for the terminator |
| **`gets(buf)`** | reads a line into `buf` with no limit; removed from the C standard in 2011 |
| **`fgets(buf, size, stdin)`** | reads at most `size - 1` characters and always adds the terminator |
| **`strcpy(dst, src)`**, **`strcat(dst, src)`** | copy or append `src`, however long it is |
| **`strncpy`** | looks bounded, but leaves out the terminator when the source is long enough |
| **`strncat`** | its size means the space **remaining**, not the buffer size |
| **`snprintf(buf, size, ...)`** | formats into `buf`, never more than `size` bytes, always terminated |
| **`strlcpy`**, **`strlcat`** | bounded copy and append that always terminate; now in glibc |
| **`sprintf`** | formats into a buffer with no size limit |
| **`scanf("%s")`** | reads a word of any length; `"%15s"` limits it to 15 characters |
| **`system(cmd)`** | runs `cmd` through the shell |
| **`execve`** | runs a program with an argument list, no shell |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=gnu17 -o name name.c` | compiles a C file; modern compilers refuse `gets` outright |
| `grep -n -E 'gets\|strcpy\|sprintf\|system' *.c` | a first scan of source code for the usual suspects |
| `python review.py` | runs your program: finds the risky function and the fix for `gets` |

### Python names

| Name | What it does |
|---|---|
| `DANGERS` | given to you: a dict from dangerous call to why it is dangerous |
| `SAFER` | given to you: a dict from dangerous call to its replacement |
| `{name: DANGERS[name] for name in called if name in DANGERS}` | a dict of only the dangerous calls, with their reasons |
| `SAFER.get(name)` | the replacement, or `None` if there is none |
| `{fn for fn, calls in functions.items() if ...}` | the names of the functions that pass the test |
| `if dangerous_calls(calls)` | true when that dict is not empty |

---

Some functions are dangerous almost wherever they appear, because their
design makes a mistake the default. Recognising them on sight, in source code
or in a binary's import list, is the fastest and most valuable kind of review
there is. It is exactly what the `gets`, `system` and `strcpy` imports in
Reversing lesson 2 were pointing at.

## Buffers, in one paragraph

C stores text in **buffers**: fixed-size areas of memory, such as
`char name[16]`, room for 15 characters and the **null terminator** (`\0`)
that marks the end of a string. C does not check that what you write fits.
Write 40 characters into that 16-byte buffer and the extra 24 land on whatever
is stored next to it in memory. That is a **buffer overflow**, and Reversing
lesson 5 shows what it overwrites.

## The usual suspects

| Call | Why it is dangerous | Safe replacement |
|---|---|---|
| `gets` | no limit at all on what it reads: a guaranteed overflow | `fgets` |
| `strcpy`, `strcat` | copy until the end of the source, with no idea of the buffer's size | `snprintf` (or `strlcpy`, `strlcat`) |
| `sprintf` | formats into a buffer with no size limit | `snprintf` |
| `system` | hands a string to the shell: Web lesson 6's command injection | `execve` with an argument list |
| `scanf("%s")` | reads a word of any length into a fixed buffer | give a width: `%15s` |

`gets` is so dangerous that it was removed from the C standard, and today's
C library does not even declare it. A modern compiler refuses the code:

```text
$ gcc -std=gnu17 -o name name.c
name.c:2:32: error: implicit declaration of function 'gets'; did you mean 'fgets'? [-Wimplicit-function-declaration]
```

Old binaries and old code still use it, which is why reviewers look for it.

### A warning about the obvious replacement

`strncpy` looks like the bounded version of `strcpy`, and is **not** a safe
one. When the source is at least as long as the limit, it copies exactly that
many bytes and **does not write a null terminator**. The next function that
reads the buffer runs off its end into whatever sits next to it.

`strncat` has a different trap: its size argument means the space
**remaining** in the buffer, not the buffer's size, an easy **off-by-one**.

`snprintf` always adds the terminator and always respects the size you give
it. `strlcpy` and `strlcat` do the same, and are now in glibc.

### The common thread

It is the one from the Web section: a call where **input decides something
the programmer assumed was fixed**:

- `gets` and `strcpy` let input decide **how many bytes** are written;
- `sprintf` with a user-supplied format lets input decide **the format**;
- `system` lets input decide **which command** runs.

## Review as a habit

A real review, of source code or of a binary's imports, is largely this:

1. Scan for the known-dangerous calls.
2. For each one, ask whether untrusted input can reach it.
3. Name the safe replacement.

Step 3 is half the job: "don't use `gets`" is only useful next to "use
`fgets` with the buffer's size". This is defensive work. You find the hole so
that it can be closed.

## Your turn

`DANGERS` (name to reason) and `SAFER` (name to replacement) are given to
you. In `review.py`:

- `dangerous_calls(called)`: a dict from each dangerous call in the list
  `called` to its reason.
- `safer_alternative(name)`: the safe replacement for a dangerous call, or
  `None`.
- `review(functions)`: given `{function_name: [calls it makes]}`, the set of
  function names that make at least one dangerous call.

Run it:

```text
risky functions: {'read_name'}
fix for gets: fgets
```

## Check yourself

1. What does `gets` do wrong?
   *It reads a line of any length into a fixed-size buffer.*
2. What should replace `gets`?
   *`fgets`, given the buffer's size.*
3. Why is `strncpy` not a safe `strcpy`?
   *It may leave out the null terminator.*
4. What does `scanf("%15s", buf)` change?
   *It reads at most 15 characters, so a 16-byte buffer is safe.*
5. What do all the dangerous calls have in common?
   *Input decides a size, a format or a command that was assumed fixed.*
