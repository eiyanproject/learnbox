---
title: "Round 1: Words"
summary: Two string functions, no library help, and a terminator to keep track of.
order: 1
files: [words.c, words.h]
run: gcc -std=c17 -Wall -c words.c
challenge:
  minutes: 12
  xp: 150
  requires:
    xp: 100
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **word** | a run of characters with no whitespace |
| **whitespace** | spaces, tabs, newlines: whatever `isspace` says |
| **trim** | remove whitespace from both ends |
| **in place** | changing the caller's string itself |
| **terminated** | ending with `'\0'` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall -c words.c` | compiles without linking, to check it builds |

### C names

| Name | What it does |
|---|---|
| `isspace((unsigned char)c)` | true for whitespace, from `<ctype.h>` |
| `const char *s` / `char *s` | a string you only read / one you may change |
| `'\0'` | the terminator |
| `memmove(dst, src, n)` | copies bytes even when the areas overlap |

---

Two small functions over C strings. The header is written; the bodies are
yours.

## The task

In `words.c`, define the two functions declared in `words.h`.

`int count_words(const char *s)` returns how many words are in `s`. A word is
a run of characters with no whitespace in it; words are separated by any
amount of whitespace (spaces, tabs, newlines - whatever `isspace` says).

```text
count_words("to be or not")      ->  4
count_words("  two   words\n")   ->  2
count_words("")                  ->  0
count_words("   ")               ->  0
```

`int trim(char *s)` removes the whitespace from both ends of `s`, **in
place**, and returns the new length. Whitespace inside the text stays.

```text
"  hello world \n"   becomes   "hello world"   and trim returns 11
"   "                becomes   ""              and trim returns 0
```

The result must still be a proper string: terminated, and starting at `s`
itself, since the caller only has that pointer.
