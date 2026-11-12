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

Every variable in Java has a type fixed when you write the code, and the
compiler checks every assignment against it. Most types are **reference
types**: the variable holds a reference to an object, such as a `String`.
Eight are **primitive types**: the variable holds the value itself, a plain
number, character or true/false, with no object around it. Primitives are
fast and small, and they come with rules about converting between them that
surprise everyone once. The exam tests the edges between the types far more
than the types themselves.

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

More bits means a bigger range: an `int` goes from about minus to plus 2.1
billion, a `long` to about 9.2 quintillion. A **literal** is a value written
directly in the code, like `42` or `1.5`. A whole-number literal is an `int`
unless it ends in `L`, and a decimal literal is a `double` unless it ends in
`f`, which is why those suffixes are needed. Underscores are allowed inside
numbers for readability: `10_000_000_000L`.

`char` holds a single character as a number (its UTF-16 code: `'A'` is 65).
Characters use single quotes, strings double quotes. And `boolean` is not a
number at all: unlike C, Java will not treat `1` as true, and
`boolean flag = 1;` is a compile error
(`incompatible types: int cannot be converted to boolean`).

### Local variables have no default value

A variable declared inside a method is a **local variable**, and Java does
not give it a starting value. Using one before assigning it is a
compile-time error, not a zero:

```text
error: variable total might not have been initialized
    System.out.println(total);
                       ^
```

Fields (variables declared in a class, outside any method) are different:
they start at `0`, `false` or `null`. The difference catches people out
because the same declaration, `int total;`, behaves differently depending on
where it is written.

You can check facts like these yourself in `jshell` (Environment lesson 1):
`Integer.MAX_VALUE`, `Byte.MIN_VALUE` or `(int) 'A'` each answer at once.

## Widening is silent, narrowing is not

**Widening** converts a value to a type with a bigger range, and can never
lose information, so Java does it automatically. **Narrowing** goes the other
way and might not fit, so Java makes you ask for it with a **cast**: the
target type in brackets before the value.

```java
int i = 10;
long l = i;        // widening: always safe, automatic
int back = (int) l; // narrowing: might lose data, so you must say so
```

(A fragment: these lines belong inside a method.) Leave out the cast, and the
code does not compile:

```text
error: incompatible types: possible lossy conversion from long to int
        int back = l;
                   ^
```

"Lossy" means some information could be lost. The compiler does not check
whether *this* value would fit; it refuses because a `long` in general might
not.

The order is `byte -> short -> int -> long -> float -> double`, with `char`
widening to `int`. Anything backwards along that chain needs a cast, and the
cast silently discards the bits that do not fit. `(int) 10_000_000_000L` keeps
only the lowest 32 bits of the 64-bit number, which happen to make
`1410065408`, as the program at the end of this lesson shows. A cast is you
telling the compiler "I know, do it anyway"; it does not check the result.

## Integer division truncates

```java
int a = 7 / 2;          // 3, not 3.5
double b = 7 / 2;       // still 3.0 - the division happened in int first
double c = 7 / 2.0;     // 3.5
```

When both operands of `/` are integer types, Java does **integer division**:
it throws the fractional part away, rounding towards zero. With at least one
`double` (or `float`) operand, it does ordinary division.

The middle line is one of the most-asked traps in the entire exam. Java works
out the right-hand side first, on its own, and only then assigns it. The
assignment type does not reach back and change how the expression was
evaluated; by the time the result is widened to double, the truncation has
already happened.

The remainder operator `%` follows the same rounding towards zero, so its
result takes the sign of the left-hand number: `7 % 2` is `1`, but `-7 % 2`
is `-1`, not `1`. (Python gives `1` there; Java and C do not.) That matters
for any "is it odd?" check: `n % 2 == 1` is false for every negative odd
number, while `n % 2 != 0` and `n % 2 == 0` are correct for all of them.

## Promotion

In any arithmetic expression, operands smaller than `int` are promoted to
`int` first. **Promotion** is a widening that Java applies automatically
while working out an expression:

```java
byte a = 10, b = 20;
byte c = a + b;         // does NOT compile: a + b is an int
byte d = (byte) (a + b);
```

The second line fails with
`incompatible types: possible lossy conversion from int to byte`: `a + b` is
an `int`, and storing an `int` in a `byte` is narrowing. The same happens with
`char`: `char next = ch + 1;` is an error, and needs `(char) (ch + 1)`.

And if either operand is larger, the whole expression widens to the larger
type: `int` plus `long` is a `long`, and `int` times `double` is a `double`.

One exception the exam loves: the compound assignment operators (`+=`, `-=`,
`*=` and so on) include a hidden cast back to the variable's type. So
`b += 1;` compiles for a `byte b`, although `b = b + 1;` does not.

## Overflow is silent

`Integer.MAX_VALUE + 1` is `Integer.MIN_VALUE`. No exception, no warning. Java
wraps, and code that assumes otherwise is wrong in a way tests rarely catch.
**Overflow** is what happens when a result is too big for its type: the
number wraps round from the largest value to the smallest, like a car's
odometer rolling over. The fix is a bigger type (`long`), or
`Math.addExact(a, b)`, which throws an `ArithmeticException` instead of
wrapping.

### Decimals are not exact

`double` stores numbers in binary, and most decimal fractions, like 0.1,
have no exact binary form, so tiny errors appear: `0.1 + 0.2` prints
`0.30000000000000004`. That is fine for measurements and fatal for money.
For exact decimal arithmetic Java has the class `java.math.BigDecimal`:
`new BigDecimal("0.1").add(new BigDecimal("0.2"))` is exactly `0.3`. (Create
it from a string, as here: `new BigDecimal(0.1)` would copy the double's
error in.)

## Increment and decrement

`i++` and `++i` both add one to `i`. They differ only in the value the
expression itself produces, which matters when the result is used in the
same statement. Predict the four printed numbers before reading the output:

```java
public class Increment {
    public static void main(String[] args) {
        int i = 5;
        int a = i++;      // a gets the OLD value, then i becomes 6
        System.out.println(a + " " + i);

        int j = 5;
        int b = ++j;      // j becomes 6 first, and b gets the NEW value
        System.out.println(b + " " + j);
    }
}
```

```output
5 6
6 6
```

Read `i++` as "use `i`, then add one" (**post-increment**) and `++i` as "add
one, then use `i`" (**pre-increment**). `i--` and `--i` work the same way
downwards. On a line of its own, `i++;` and `++i;` do exactly the same thing;
the exam puts them inside larger expressions, where they do not.

`i++` is itself three steps, read `i`, add one, write `i` back, which
matters when several threads share a variable (Gold lesson 6).

## Every rule above, run

Predict each printed line before you read the output below the program:

```java
public class Promotion {
    public static void main(String[] args) {
        int a = 7 / 2;
        double b = 7 / 2;
        double c = 7 / 2.0;
        System.out.println(a + " " + b + " " + c);

        long big = 10_000_000_000L;
        System.out.println((int) big);           // the high bits are thrown away
        System.out.println(Integer.MAX_VALUE + 1);

        byte x = 10, y = 20;
        System.out.println((byte) (x + y) + " " + (byte) 200);

        char ch = 'A';
        int code = ch;                            // char widens to int
        System.out.println(code + " " + (char) (code + 1));
    }
}
```

```output
3 3.0 3.5
1410065408
-2147483648
30 -56
65 B
```

Line by line: integer division gives 3 twice, once printed as a `double`
(`3.0`). The cast of ten billion keeps only its low 32 bits. `MAX_VALUE + 1`
wraps to the most negative `int`. `(byte) 200` does not fit in a byte's -128
to 127, so it wraps too, to -56 (200 - 256). And `'A'` is the number 65, so
adding 1 and casting back gives `'B'`.

Inside `println`, `+` with a string on either side means "join as text", and
Java reads `+` from left to right. That is why `a + " " + b` prints the values
with a space between them rather than adding them.

## Your turn

In `Numbers.java`:

- `public static double averageOf(int a, int b)` — the true average, not
  truncated: `averageOf(7, 2)` is `4.5`, and `averageOf(-2, -3)` is `-2.5`
- `public static int narrow(long value)` — the value as an `int`, cast
  explicitly. Small values come through unchanged; for a value too big for an
  `int`, the high bits are dropped: `narrow(4294967303L)` (2³² + 7) is `7`
- `public static int overflowed()` — `Integer.MAX_VALUE + 1`, which the tests
  expect to be `Integer.MIN_VALUE`
- `public static boolean isEven(int n)` — correct for negative numbers too:
  `isEven(-4)` is `true`, `isEven(-3)` is `false`
- `public static char nextLetter(char c)` — the next character:
  `nextLetter('a')` is `'b'`. Remember that `c + 1` is an `int`.
