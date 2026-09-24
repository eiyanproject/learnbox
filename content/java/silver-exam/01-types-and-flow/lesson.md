---
title: "Paper 1: types, operators and flow"
summary: Cumulative questions over the first half of Silver, with the promotion and truncation traps the real paper leans on.
order: 1
files: [Paper1.java]
run: javac Paper1.java && java Paper1
hints:
  - "`evaluate` must return 3 for (7, 2): the exam's point is that int division truncates before any widening happens."
  - "`promote` returns the TYPE NAME that `a + b` produces. byte + byte is int; int + long is long; anything with a double is double. Return the string, do not compute the value."
  - "`ternaryChain` is `n < 0 ? \"negative\" : n == 0 ? \"zero\" : \"positive\"` - the ternary is right-associative, which is what makes chaining work."
  - "`fizzOrBuzz` uses a switch on a computed key, or plain if/else - either is fine, but check the combined case first."
---

No new material. These are the Silver objectives from the first four lessons,
mixed and without labels, written the way the exam writes them: short methods
where the answer depends on one rule you either know or do not.

## The rules being tested

Worth a re-read before you start, because each appears at least once:

- **Integer division truncates**, and the assignment type does not reach back
  and change that. `double d = 7 / 2` is `3.0`.
- **Promotion goes up, never down.** Anything narrower than `int` is promoted
  to `int` in arithmetic; if either operand is wider, the whole expression
  becomes the wider type.
- **Overflow wraps silently.** `Integer.MAX_VALUE + 1` is negative.
- **`%` keeps the sign of the left operand.** `-7 % 3` is `-1`.
- **The ternary is right-associative**, so `a ? x : b ? y : z` parses as
  `a ? x : (b ? y : z)` and chains naturally.
- **Compound assignment casts implicitly.** `byte b = 10; b += 300;` compiles
  and gives a wrapped value, where `b = b + 300` does not compile at all. This
  one catches almost everyone.

## Your turn

In `Paper1.java`:

- `public static int evaluate(int a, int b)` — return `a / b` using integer
  division
- `public static String promote(String leftType, String rightType)` — given two
  of `"byte"`, `"short"`, `"int"`, `"long"`, `"float"`, `"double"`, return the
  type their sum has
- `public static String ternaryChain(int n)` — `"negative"`, `"zero"` or
  `"positive"`, written as a chained ternary
- `public static String fizzOrBuzz(int n)` — `"FizzBuzz"`, `"Fizz"`, `"Buzz"`
  or the number as a string
- `public static byte compound(byte start, int add)` — the result of
  `start += add`, which wraps rather than failing
