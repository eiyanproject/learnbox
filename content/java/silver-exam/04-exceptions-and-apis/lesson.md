---
title: "Paper 4: exceptions and the core APIs"
summary: Which exception wins, what finally does to a return, and the boxing and date rules from the last lesson.
order: 4
files: [Paper4.java]
run: javac Paper4.java && java Paper4
hints:
  - "`finallyWins` should return the value from the finally block - a return in finally replaces the one from try, discarding it."
  - "`classify` returns the exception's simple name: `e.getClass().getSimpleName()`, and `\"none\"` when nothing is thrown."
  - "`sumOrNull` must not unbox a null - check each Integer for null before adding, and return null if any of them is null."
  - "`isLeap` can use `java.time.Year.isLeap(year)` or the rule directly: divisible by 4, except centuries unless divisible by 400."
---

The last paper collects exceptions and the core API behaviour from lesson
eight — the two areas where the exam most often shows you code and asks what it
prints.

## Worth re-reading

- **Checked must be handled or declared; unchecked need not be.** Everything
  under `RuntimeException` is unchecked.
- **Catch narrowest first.** A broader type above a narrower one is a compile
  error, not a warning.
- **`NumberFormatException extends IllegalArgumentException`**, which is why a
  catch for the latter also catches the former.
- **`finally` always runs**, and a `return` inside it replaces the one from
  `try` — including discarding an exception that was on its way out. It is
  legal and it is a mistake.
- **try-with-resources closes in reverse order**, before catch or finally.
- **`Integer` caches -128..127**, so `==` on boxed values is unreliable.
- **Unboxing null throws `NullPointerException`** on a line that looks like
  plain arithmetic.
- **`java.time` types are immutable**; every method returns a new value.

## Your turn

In `Paper4.java`:

- `public static int finallyWins()` — a method whose `try` returns 1 and whose
  `finally` returns 2, demonstrating which one the caller sees
- `public static String classify(Runnable action)` — the simple name of
  whatever it throws, or `"none"`
- `public static Integer sumOrNull(Integer a, Integer b)` — their sum, or
  `null` if either is null
- `public static boolean isLeap(int year)`
- `public static String monthName(int month)` — `"JANUARY"` for 1, throwing
  `java.time.DateTimeException` for an invalid month
