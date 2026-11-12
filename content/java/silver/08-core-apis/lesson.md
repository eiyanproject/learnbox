---
title: Wrappers, autoboxing and dates
summary: The object versions of the primitives, the caching that makes == lie, var, records, and the immutable date API.
order: 8
files: [Core.java]
run: javac Core.java && java Core
hints:
  - "`boxedEquals` must compare with `.equals()`. Integer caches -128..127, so == is true for small values and false above that - the test uses 1000 deliberately."
  - "`safeUnbox` takes an Integer that may be null: returning `value` directly would throw NullPointerException on unboxing, so check for null first."
  - "`daysBetween` uses `java.time.temporal.ChronoUnit.DAYS.between(a, b)`."
  - "`Point` is a record: `record Point(int x, int y) {}` gives you the constructor, accessors `x()` and `y()`, equals, hashCode and toString."
---

This lesson collects four parts of the core library that every Java program
uses and the Silver exam tests: the wrapper classes and the automatic
conversions that make `==` misbehave, `var` for shorter declarations, records
for small data classes, and the `java.time` date API. Each one hides a trap
that compiles fine and fails later, so each section ends with the trap.

## The wrappers

Every primitive has an object counterpart: `int`/`Integer`,
`double`/`Double`, `char`/`Character`, `boolean`/`Boolean`, and so on.
Collections hold objects, not primitives, so wrappers are how an `int` gets
into a `List`.

**Autoboxing** converts between them automatically:

```java
Integer boxed = 5;       // autoboxing
int back = boxed;        // unboxing
```

Two traps, both examined:

```java
Integer a = 127, b = 127;
a == b          // true

Integer c = 1000, d = 1000;
c == d          // false
```

(Fragments: the comments give each expression's value; the program at the
end of the lesson prints them.)

An `Integer` is an object, so `==` compares references, exactly as with
`String` (Silver 2). Java caches boxed integers from -128 to 127: boxing any
value in that range returns the same shared object every time, so `==`
accidentally works for small numbers. Above the range, each boxing creates a
new object, and `==` fails. Use `equals`, which compares the values.

```java
Integer maybe = null;
int n = maybe;           // NullPointerException, on the unboxing
```

Unboxing null throws, and the line looks like a plain assignment. Unboxing
calls a method on the `Integer` (`maybe.intValue()`, inserted by the
compiler), and calling a method on `null` is what `NullPointerException`
means. Any arithmetic on a nullable `Integer` carries this risk, as does
`int count = map.get(key);` when the key is missing, since `get` then returns
`null`. Check for `null` before unboxing.

## var

```java
var names = new ArrayList<String>();    // inferred as ArrayList<String>
```

`var` (Java 10) lets the compiler work out a local variable's type from the
value it is given, so you do not have to write the type twice. `var` is
**inference**, not dynamic typing: the type is fixed at compile time, exactly
as if you had written it, and assigning a different type later is still an
error. `var names = ...` above *is* an `ArrayList<String>`; `names = 5;`
fails with `incompatible types: int cannot be converted to ArrayList<String>`.

It is only allowed for local variables with an initialiser — not fields, not
parameters, not return types, and never `var x = null` (there is no type to
infer from `null`), nor `var x;` with no value at all. Use it where the type
is obvious from the right-hand side; where it is not, writing the type helps
the reader.

## Records

```java
record Point(int x, int y) {}
```

A **record** (Java 16) is a class whose job is to carry some data. Here is
the essence-versus-ceremony comparison: the one line above does the same as
roughly this much ordinary class:

```java
final class Point {
    private final int x;
    private final int y;

    Point(int x, int y) { this.x = x; this.y = y; }

    int x() { return x; }
    int y() { return y; }

    @Override public boolean equals(Object o) {
        return o instanceof Point p && p.x == x && p.y == y;
    }
    @Override public int hashCode() { return 31 * x + y; }
    @Override public String toString() { return "Point[x=" + x + ", y=" + y + "]"; }
}
```

One line gives a final class, private final fields, a canonical constructor,
accessors named `x()` and `y()` (no `get` prefix), plus `equals`, `hashCode`
and `toString`. The **canonical constructor** is the one taking every
component in order: `new Point(1, 2)`. Records are immutable and cannot
extend a class (they can implement interfaces, and can have extra methods of
their own). `hashCode` is the number hash-based collections such as
`HashMap` use to find an object; equal objects must have equal hash codes,
which the record guarantees.

Add validation with a compact constructor:

```java
record Point(int x, int y) {
    Point {
        if (x < 0) throw new IllegalArgumentException();
    }
}
```

A **compact constructor** has no parameter list. Its body runs before the
fields are assigned, with the parameters already available by their
component names, and the assignments happen automatically afterwards. It is
the place for checks, so an invalid `Point` can never exist.

## java.time

```java
LocalDate d = LocalDate.of(2026, 9, 24);
LocalDate later = d.plusDays(10);       // a NEW date; d is unchanged
```

(A fragment.) The `java.time` package (Java 8) is the modern date and time
API. Every type here is **immutable**, so every method returns a new value.
Ignoring the return is the same mistake as with String. `LocalDate`,
`LocalTime`, `LocalDateTime`, `Duration` (time-based) and `Period`
(date-based) are the ones the exam expects:

| Type | Holds | Example |
|---|---|---|
| `LocalDate` | a date, no time or time zone | `2026-09-24` |
| `LocalTime` | a time of day | `14:30` |
| `LocalDateTime` | both | `2026-09-24T14:30` |
| `Duration` | an amount of time in seconds and nanoseconds | `PT2H` (2 hours) |
| `Period` | an amount of time in years, months and days | `P1M` (1 month) |

"Local" means no time zone: a wall-clock date or time.
`ChronoUnit.DAYS.between(a, b)` counts the days from `a` to `b`, and is
negative if `b` is earlier.

Months are 1-based and sane, unlike the old `Calendar` API, where January was
month 0: `LocalDate.of(2026, 9, 24)` really is 24 September.

## Run

All four traps in one program. Predict each line, then check; you can also
try any single line in `jshell`, for example `Integer a = 1000, b = 1000; a == b`.

```java
import java.time.LocalDate;

public class CoreApis {
    record Point(int x, int y) {}

    public static void main(String[] args) {
        Integer a = 127, b = 127, c = 1000, d = 1000;
        System.out.println((a == b) + " " + (c == d) + " " + c.equals(d));

        Integer maybe = null;
        try {
            int n = maybe;
        } catch (NullPointerException e) {
            System.out.println("unboxing null threw");
        }

        Point p = new Point(1, 2);
        System.out.println(p + " " + p.x() + " " + p.equals(new Point(1, 2)));

        LocalDate day = LocalDate.of(2026, 9, 24);
        day.plusDays(10);                        // result ignored: day is unchanged
        System.out.println(day + " " + day.plusDays(10) + " " + day.getDayOfWeek());
    }
}
```

```output
true false true
unboxing null threw
Point[x=1, y=2] 1 true
2026-09-24 2026-10-04 THURSDAY
```

`127` is inside the cache, so `a == b` is true; `1000` is not, so `c == d` is
false while `equals` is true. Unboxing `null` threw. The record printed itself
with the generated `toString`, and `equals` compared the values. And
`day.plusDays(10)` on its own line did nothing to `day`; only the second call,
whose result is printed, shows the later date.

## Your turn

In `Core.java`:

- `public static boolean boxedEquals(Integer a, Integer b)` — content, not
  identity. The tests use 1000, outside the cache.
- `public static int safeUnbox(Integer value, int fallback)` — the value, or
  the fallback when it is `null`
- `public static long daysBetween(LocalDate a, LocalDate b)` — the number of
  days from `a` to `b`: 1 September to 11 September is `10`, the reverse is
  `-10`, and 1 January to 1 February is `31`
- `public static LocalDate addWeeks(LocalDate date, int weeks)` — a new date
  that many weeks later; `date` itself must not change
- a `record Point(int x, int y)` declared **inside** the `Core` class (the
  tests use it as `Core.Point`), with a `double distanceFromOrigin()` method:
  the square root of `x * x + y * y`, so `new Point(3, 4)` gives `5.0`
  (`Math.sqrt` computes square roots)
