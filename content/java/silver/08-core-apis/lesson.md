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

Java caches boxed integers from -128 to 127, so `==` accidentally works for
small numbers and fails for large ones. Use `equals`.

```java
Integer maybe = null;
int n = maybe;           // NullPointerException, on the unboxing
```

Unboxing null throws, and the line looks like a plain assignment. Any
arithmetic on a nullable `Integer` carries this risk.

## var

```java
var names = new ArrayList<String>();    // inferred as ArrayList<String>
```

`var` is inference, not dynamic typing: the type is fixed at compile time. It
is only allowed for local variables with an initialiser — not fields, not
parameters, not return types, and never `var x = null`.

## Records

```java
record Point(int x, int y) {}
```

One line gives a final class, private final fields, a canonical constructor,
accessors named `x()` and `y()` (no `get` prefix), plus `equals`, `hashCode`
and `toString`. Records are immutable and cannot extend a class.

Add validation with a compact constructor:

```java
record Point(int x, int y) {
    Point {
        if (x < 0) throw new IllegalArgumentException();
    }
}
```

## java.time

```java
LocalDate d = LocalDate.of(2026, 9, 24);
LocalDate later = d.plusDays(10);       // a NEW date; d is unchanged
```

Every type here is **immutable**, so every method returns a new value. Ignoring
the return is the same mistake as with String. `LocalDate`, `LocalTime`,
`LocalDateTime`, `Duration` (time-based) and `Period` (date-based) are the ones
the exam expects.

Months are 1-based and sane, unlike the old `Calendar` API.

## Your turn

In `Core.java`:

- `public static boolean boxedEquals(Integer a, Integer b)` — content, not
  identity
- `public static int safeUnbox(Integer value, int fallback)` — the fallback
  when null
- `public static long daysBetween(LocalDate a, LocalDate b)`
- `public static LocalDate addWeeks(LocalDate date, int weeks)`
- a `record Point(int x, int y)` with a `distanceFromOrigin()` method
