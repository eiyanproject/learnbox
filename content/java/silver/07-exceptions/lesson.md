---
title: Exceptions, finally and try-with-resources
summary: Checked against unchecked, the order of catch blocks, what finally really guarantees, and the construct that replaced it.
order: 7
files: [Safe.java]
run: javac Safe.java && java Safe
hints:
  - "`parseOrDefault` catches NumberFormatException - which is unchecked, so nothing forces you to catch it, but catching it here is the point."
  - "`divide` should throw ArithmeticException for a zero divisor. Integer division by zero already throws it, so letting it happen is a legitimate answer."
  - "`describe` must catch the more specific exception FIRST: a catch for Exception above one for IllegalArgumentException does not compile."
  - "`closeOrder` uses try-with-resources with two resources - they are closed in REVERSE order of declaration, which is what the test checks."
---

## The hierarchy

```
Throwable
 ├── Error                    (OutOfMemoryError, StackOverflowError - do not catch)
 └── Exception
      ├── RuntimeException    unchecked: NullPointer, IllegalArgument, Arithmetic...
      └── everything else     checked: IOException, SQLException...
```

**Checked** exceptions must be caught or declared with `throws`; the compiler
enforces it. **Unchecked** ones — anything under `RuntimeException`, plus
`Error` — need neither.

The division is about intent: checked means "this can fail for reasons outside
your control, deal with it"; unchecked means "this is a bug, fix the code".

## try, catch, finally

```java
try {
    risky();
} catch (FileNotFoundException e) {   // most specific first
    ...
} catch (IOException e) {
    ...
} finally {
    cleanup();                        // runs either way
}
```

Catch blocks are tried **in order**, and a broader type above a narrower one is
a compile error — unreachable code. This is checked at compile time, which
makes it a reliable exam question.

Multi-catch handles unrelated types together:

```java
catch (NumberFormatException | ArithmeticException e)
```

The variable is effectively final there, and the types may not overlap.

## What finally guarantees

`finally` runs whether or not an exception was thrown, **and even if the try
block returns**. A `return` inside `finally` replaces the one from `try`,
discarding the original — and discarding any in-flight exception with it, which
is why it is considered a mistake rather than a technique.

## try-with-resources

```java
try (Scanner in = new Scanner(file); PrintWriter out = new PrintWriter(dest)) {
    ...
}
```

Anything implementing `AutoCloseable` is closed automatically, **in reverse
order of declaration**, before any catch or finally runs. Resources are
implicitly final. This is strictly better than closing in `finally`, where an
exception during close can mask the real one — here the close exception is
*suppressed* and attached to the original, retrievable with
`getSuppressed()`.

## Your turn

In `Safe.java`:

- `public static int parseOrDefault(String s, int fallback)` — the parsed int,
  or the fallback if it will not parse
- `public static int divide(int a, int b)` — throws `ArithmeticException` when
  `b` is zero
- `public static String describe(Runnable action)` — runs it and returns
  `"ok"`, `"bad argument"` for an `IllegalArgumentException`, or `"failed"` for
  any other exception
- `public static String closeOrder()` — uses try-with-resources with two
  `AutoCloseable`s and returns the order they closed in, e.g. `"B,A"`
