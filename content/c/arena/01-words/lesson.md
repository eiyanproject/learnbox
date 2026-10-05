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
