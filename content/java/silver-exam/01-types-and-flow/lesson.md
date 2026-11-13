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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **exam paper** | mixed questions over earlier lessons, with no new material |
| **integer division** | `/` on two whole numbers truncates towards zero, before any widening (Silver lesson 1) |
| **truncate** | drop the fraction: `7 / 2` is 3, `-7 / 2` is -3 |
| **promotion** | operands smaller than `int` become `int`; a wider operand widens the whole expression |
| **overflow** | a result too big for its type wraps round silently |
| **remainder** (`%`) | keeps the sign of the left operand: `-7 % 3` is -1 |
| **ternary operator** | `c ? x : y`; it is **right-associative**, so `a ? x : b ? y : z` means `a ? x : (b ? y : z)` |
| **compound assignment** | `+=` and friends cast back to the variable's type: `b += 300` on a `byte` wraps to 54 |
| **type name** | here, a string such as `"int"` naming the type an expression has |
| **FizzBuzz** | the classic exercise: "Fizz" for multiples of 3, "Buzz" for 5, "FizzBuzz" for both |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Paper1.java && java Paper1` | builds and runs this paper's file |

### Java names

| Name | What it does |
|---|---|
| `byte`, `short`, `int`, `long`, `float`, `double` | the numeric primitive types, narrowest to widest |
| `Integer.MAX_VALUE + 1` | wraps to `Integer.MIN_VALUE` |
| `(byte) x` | a narrowing cast |
| `n % 15 == 0` | divisible by both 3 and 5 |
| `String.valueOf(n)` | a number as text, such as `"7"` |

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

Each rule, as a line of output. Treat it as a practice question: cover the output, write down what you expect each line to be, then compare.

```java
public class Rules {
    public static void main(String[] args) {
        double d = 7 / 2;
        System.out.println(d);
        System.out.println(Integer.MAX_VALUE + 1);
        System.out.println(-7 % 3);
        int a = 5;
        System.out.println(a > 3 ? "big" : a > 1 ? "medium" : "small");
        byte b = 10;
        b += 300;                  // (byte) (10 + 300)
        System.out.println(b);
    }
}
```

```output
3.0
-2147483648
-1
big
54
```

The working for each line:

- `7 / 2` is integer division, `3`, and only then widened to `3.0`.
- `MAX_VALUE + 1` wraps round to the most negative `int`.
- `-7 % 3`: `-7 / 3` truncates towards zero to `-2`, and `-2 * 3` is `-6`,
  so the remainder is `-7 - (-6)`, which is `-1`. It takes the sign of the
  left operand.
- `a > 3` is true, so the first branch wins and the rest of the chain is
  never looked at.
- `b += 300` computes `10 + 300 = 310` as an `int`, then casts it back to
  `byte`. A byte holds -128 to 127, so 310 wraps: `310 - 256` is `54`.

The promotion rules as a table, for the `promote` question below. The result
is the wider of the two operand types, but never narrower than `int`:

| Left | Right | Result |
|---|---|---|
| `byte` | `byte` | `int` |
| `short` | `byte` | `int` |
| `int` | `long` | `long` |
| `long` | `float` | `float` |
| `int` | `double` | `double` |

`long` plus `float` is a `float`, even though a `long` has more bits: in the
widening order, `float` comes after `long`, because it covers a much wider
range of values (with less precision).

## Your turn

In `Paper1.java`:

- `public static int evaluate(int a, int b)` — return `a / b` using integer
  division: `evaluate(7, 2)` is `3`, and `evaluate(-7, 2)` is `-3`, because
  Java truncates towards zero
- `public static String promote(String leftType, String rightType)` — given two
  of `"byte"`, `"short"`, `"int"`, `"long"`, `"float"`, `"double"`, return the
  name of the type their sum has, as a string, by the table above:
  `promote("byte", "byte")` is `"int"`. Do not compute any sums; this is a
  question about the rule.
- `public static String ternaryChain(int n)` — `"negative"`, `"zero"` or
  `"positive"`, written as a chained ternary
- `public static String fizzOrBuzz(int n)` — `"FizzBuzz"` for multiples of 15,
  `"Fizz"` for other multiples of 3, `"Buzz"` for other multiples of 5, or the
  number as a string (`"7"`)
- `public static byte compound(byte start, int add)` — the result of
  `start += add`, which wraps rather than failing: `compound((byte) 10, 300)`
  is `54`
