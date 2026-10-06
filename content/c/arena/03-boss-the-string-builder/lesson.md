---
title: "Boss: The string builder"
summary: A string that grows. malloc, realloc, a terminator that must always be there, and nothing leaked.
order: 4
files: [str.c, str.h]
run: gcc -std=c17 -Wall -c str.c
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 550
---

Fixed buffers have run out of road. The report generator needs a string it
can keep adding to, and it needs it in half an hour.

## The task

`str.h` defines the struct and declares the functions. Define them in
`str.c`. Do not change the header.

```c
typedef struct {
    char *data;   /* heap buffer, always NUL-terminated */
    size_t len;   /* characters in the string, not counting the terminator */
    size_t cap;   /* bytes allocated; always greater than len */
} Str;
```

Three things must be true after every successful call: `data` points to a
buffer of `cap` bytes, `data[len]` is the terminator, and `cap > len`.

- `int str_init(Str *s)` sets up an empty string `""` with a small buffer.
- `int str_append(Str *s, const char *text)` adds `text` to the end.
- `int str_append_char(Str *s, char c)` adds one character.
- `int str_insert(Str *s, size_t at, const char *text)` puts `text` in so
  that it starts at index `at`, moving what was there to the right. `at`
  equal to `len` is an append. `at` greater than `len` is an error.
- `void str_clear(Str *s)` makes the string empty again and keeps the
  buffer.
- `void str_free(Str *s)` frees the buffer and sets `data` to `NULL` and
  `len` and `cap` to `0`. Calling it twice must be safe.

The three functions that return `int` return `0` on success and `-1` on
failure - an allocation that failed, or a bad `at` - and a failed call leaves
the string exactly as it was.

Grow the buffer with `realloc` when the text does not fit. Doubling it is
the usual way; growing by exactly what is needed each time also passes, but
the tests append a few thousand times.

```text
str_init(&s);                 ""
str_append(&s, "world");      "world"
str_insert(&s, 0, "hello ");  "hello world"
str_append_char(&s, '!');     "hello world!"
```
