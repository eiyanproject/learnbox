---
title: Strings are arrays with a rule
summary: The NUL terminator, why strlen is a loop, and the buffer overflows that come from forgetting the byte nobody counts.
order: 3
files: [str.c, str.h]
run: gcc -std=c17 -Wall str.c -o str && ./str
hints:
  - "`my_strlen` walks until it finds '\\0' and does not count it - a plain while loop over an index."
  - "`copy_into` must never write more than `size` bytes INCLUDING the terminator, so the most characters it can copy is size - 1."
  - "`count_char` is a simple loop; `reverse_in_place` swaps from both ends towards the middle."
  - "Return the number of characters copied from `copy_into`, and 0 if size is 0 - there is not even room for the terminator then."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **string** | an array of `char` ending with a `'\0'` byte |
| **terminator** | the `'\0'` byte that marks the end |
| **string literal** | `"ada"` written in the code; writing to one is undefined behaviour |
| **buffer** | an array used to hold data |
| **buffer overflow** | writing past the end of a buffer, corrupting what follows |
| **O(n)**, **O(n²)** | time growing with the length / with its square |
| **destination** / **source** | where text is copied to / from |
| **`const`** | a promise not to change what the pointer points at |
| **in place** | changing the original instead of making a copy |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall str.c -o str && ./str` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `'\0'` | the terminator byte |
| `char name[] = "ada";` | four bytes: three letters and the terminator |
| `strlen(s)` | counts characters up to the terminator |
| `strcpy(dst, src)` | copies with no size check: overflows |
| `strncpy(dst, src, n)` | does not terminate when the source is too long: a trap |
| `memcpy(dst, src, n)` | copies exactly `n` bytes |
| `snprintf(dst, size, "%s", src)` | copies at most `size - 1` characters and always terminates |
| `sizeof dst` | the buffer's size, where the array is visible |
| `const char *s` | a string the function only reads |

---

C has no string type. A "string" is an array of `char` with a `'\0'` byte at
the end, and every function in `<string.h>` depends on that byte being there.

```c
char name[] = "ada";     /* four bytes: 'a' 'd' 'a' '\0' */
```

`sizeof(name)` is 4. `strlen(name)` is 3. The difference is the terminator, and
almost every C string bug is that difference being forgotten.

## strlen is a loop

```c
size_t my_strlen(const char *s) {
    size_t n = 0;
    while (s[n] != '\0') n++;
    return n;
}
```

It walks until it finds the terminator. So:

- `strlen` is O(n), and calling it inside a loop condition makes that loop
  O(n²).
- If the terminator is missing, it keeps reading past the end of the buffer —
  into whatever happens to be there.

## The overflow

```c
char small[8];
strcpy(small, "a rather long string");   /* writes 21 bytes into 8 */
```

This compiles with no warning and corrupts whatever follows `small` in memory.
It is the single most exploited bug class in the history of software.

The fix is to always know the size of your destination and never write more:

```c
size_t n = strlen(src);
if (n >= size) n = size - 1;    /* leave room for the terminator */
memcpy(dst, src, n);
dst[n] = '\0';
```

`strncpy` exists and is a trap: it does **not** terminate the destination when
the source is too long. `snprintf(dst, size, "%s", src)` always terminates and
is the safer habit:

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char name[] = "ada";
    printf("sizeof=%zu strlen=%zu\n", sizeof(name), strlen(name));

    char dst[8];
    snprintf(dst, sizeof dst, "%s", "a rather long string");
    printf("\"%s\" (%zu bytes + terminator)\n", dst, strlen(dst));
    return 0;
}
```

```output
sizeof=4 strlen=3
"a rathe" (7 bytes + terminator)
```

Cut short, but terminated - and nothing written past `dst`.

## const char * means do not write

```c
size_t my_strlen(const char *s);
```

`const` here is a promise to the caller that the function only reads. It also
means string literals are safe to pass — writing to one is undefined behaviour,
and the `const` makes the compiler stop you.

## Your turn

In `str.h` and `str.c`:

- `int my_strlen(const char *s)`
- `int copy_into(char *dst, int size, const char *src)` — copies as much as
  fits, always terminates, returns the number of characters copied
- `int count_char(const char *s, char c)`
- `void reverse_in_place(char *s)`
