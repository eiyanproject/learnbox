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

Each rule, as a line of output, plus one `java.time` edge the exam likes. Treat it as a practice question: cover the output, write down what you expect each line to be, then compare.

```java
import java.time.LocalDate;

public class ExamApis {
    @SuppressWarnings("finally")
    static int f() {
        try {
            throw new IllegalStateException();
        } finally {
            return 7;
        }
    }

    public static void main(String[] args) {
        try {
            Integer.parseInt("x");
        } catch (IllegalArgumentException e) {
            System.out.println(e.getClass().getSimpleName());
        }
        System.out.println(f());
        Integer a = 128, b = 128;
        System.out.println(a == b);
        LocalDate d = LocalDate.of(2026, 1, 31);
        d.plusMonths(1);
        System.out.println(d + " " + d.plusMonths(1));   // no February 31st
    }
}
```

```output
NumberFormatException
7
false
2026-01-31 2026-02-28
```

`parseInt("x")` throws `NumberFormatException`, and the `catch` for its
parent `IllegalArgumentException` catches it. `f()` throws, but the `return`
in `finally` replaces the exception with 7. `128` is just outside the
`Integer` cache, so the two boxes are different objects. And adding a month
to 31 January cannot give 31 February, so `plusMonths` clamps to the last
valid day of that month, 28 February (29 in a leap year), rather than
throwing or spilling into March. The bare `d.plusMonths(1);` line changes
nothing, as always with immutable types.

## Your turn

In `Paper4.java`:

- `public static int finallyWins()` — a method whose `try` returns 1 and whose
  `finally` returns 2, demonstrating which one the caller sees
- `public static String classify(Runnable action)` — run it, and return the
  simple class name of whatever it throws (`"IllegalStateException"`,
  `"NumberFormatException"`, `"ArithmeticException"`), or `"none"` if it
  throws nothing. Report the actual class, not a parent:
  `e.getClass().getSimpleName()` does that.
- `public static Integer sumOrNull(Integer a, Integer b)` — their sum, or
  `null` if either is null. Note the return type is `Integer`, so `null` is a
  possible result; check before you add, since adding unboxes both.
- `public static boolean isLeap(int year)` — 2024 and 2000 are leap years;
  2023, 1900 and 2026 are not
- `public static String monthName(int month)` — the month's name in capitals,
  `"JANUARY"` for 1 and `"DECEMBER"` for 12, throwing
  `java.time.DateTimeException` for an invalid month such as 0 or 13.
  `java.time.Month.of(month)` does both: it returns the enum constant, whose
  `name()` is the capitalised name, and throws for anything outside 1 to 12.
