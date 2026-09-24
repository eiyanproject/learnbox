---
title: Primitives, casting and operator traps
summary: The eight primitives, what widens silently and what needs a cast, integer division, and the promotion rules the exam builds questions on.
order: 1
files: [Numbers.java]
run: javac Numbers.java && java Numbers
hints:
  - "`averageOf(int, int)` must not truncate: divide by 2.0, or cast one operand, or the arithmetic happens in int before it ever becomes a double."
  - "`narrow(long)` needs an explicit `(int)` cast - long does not fit in int, so the compiler refuses to do it silently."
  - "`overflowed()` should return Integer.MAX_VALUE + 1, which wraps to Integer.MIN_VALUE. Java does not throw on integer overflow."
  - "`isEven` can use `n % 2 == 0`, and it must work for negative numbers too - in Java -3 % 2 is -1, not 1, so comparing to 1 would be wrong."
---

Java has eight primitive types, and the exam tests the edges between them far
more than the types themselves.

| Type | Bits | Notes |
|---|---|---|
| `byte` | 8 | -128 to 127 |
| `short` | 16 | |
| `int` | 32 | the default for integer literals |
| `long` | 64 | literal needs `L`: `10000000000L` |
| `float` | 32 | literal needs `f`: `1.5f` |
| `double` | 64 | the default for decimal literals |
| `char` | 16 | unsigned, holds one UTF-16 unit |
| `boolean` | — | only `true` / `false`, never 0 or 1 |

## Widening is silent, narrowing is not

```java
int i = 10;
long l = i;        // widening: always safe, automatic
int back = (int) l; // narrowing: might lose data, so you must say so
```

The order is `byte -> short -> int -> long -> float -> double`, with `char`
widening to `int`. Anything backwards along that chain needs a cast, and the
cast silently discards the bits that do not fit.

## Integer division truncates

```java
int a = 7 / 2;          // 3, not 3.5
double b = 7 / 2;       // still 3.0 - the division happened in int first
double c = 7 / 2.0;     // 3.5
```

The middle line is one of the most-asked traps in the entire exam. The
assignment type does not reach back and change how the expression was
evaluated; by the time the result is widened to double, the truncation has
already happened.

## Promotion

In any arithmetic expression, operands smaller than `int` are promoted to
`int` first:

```java
byte a = 10, b = 20;
byte c = a + b;         // does NOT compile: a + b is an int
byte d = (byte) (a + b);
```

And if either operand is larger, the whole expression widens to the larger
type.

## Overflow is silent

`Integer.MAX_VALUE + 1` is `Integer.MIN_VALUE`. No exception, no warning. Java
wraps, and code that assumes otherwise is wrong in a way tests rarely catch.

## Your turn

In `Numbers.java`:

- `public static double averageOf(int a, int b)` — the true average, not
  truncated
- `public static int narrow(long value)` — the value as an `int`, cast
  explicitly
- `public static int overflowed()` — `Integer.MAX_VALUE + 1`
- `public static boolean isEven(int n)` — correct for negative numbers too
- `public static char nextLetter(char c)` — the next character
