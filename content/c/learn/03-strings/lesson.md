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
is the safer habit.

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
