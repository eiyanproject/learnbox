---
title: "Paper 2: strings, arrays and equality"
summary: The immutability and identity questions, plus the array traps - length against length(), and equals against Arrays.equals.
order: 2
files: [Paper2.java]
run: javac Paper2.java && java Paper2
hints:
  - "`chained` shows that String methods return new strings: apply them in order and return the result, e.g. `s.trim().replace(\" \", \"_\").toUpperCase()`."
  - "`identical` must return whether the two are the SAME OBJECT - use ==. `equivalent` must compare content with equals. The test contrasts them deliberately."
  - "`sameElements` needs `java.util.Arrays.equals(a, b)`, because a.equals(b) on arrays compares references."
  - "`describe` returns e.g. `\"[1, 2, 3] len=3\"` - use Arrays.toString, since printing an array directly gives something like [I@1b6d3586."
---

The second paper covers strings, arrays and the equality rules that sit under
both. The recurring theme is the difference between **being the same object**
and **holding the same value** — Java distinguishes them everywhere, and the
exam asks about it constantly.

## Worth re-reading

- **String is immutable.** Every method returns a new one. `s.toUpperCase();`
  on its own line is a no-op.
- **`==` on references is identity.** For strings it *appears* to work because
  literals are pooled; anything built at runtime breaks it.
- **Arrays use `length`, strings use `length()`.** One field, one method.
- **`array.equals(other)` is reference equality.** `Arrays.equals` compares
  elements; `Arrays.deepEquals` handles nesting.
- **Printing an array** gives its type and hash, not its contents.
- **`substring(a, b)` excludes `b`**, so the result is `b - a` characters long.
- **`split` takes a regex**, so splitting on `"."` matches every character
  unless you escape it.

Each rule, as a line of output. Treat it as a practice question: cover the output, write down what you expect each line to be, then compare.

```java
import java.util.Arrays;

public class Equality {
    public static void main(String[] args) {
        String s = "java";
        s.toUpperCase();
        System.out.println(s);
        String built = new StringBuilder("ja").append("va").toString();
        System.out.println((s == built) + " " + s.equals(built));

        int[][] x = {{1}}, y = {{1}};
        System.out.println(x.equals(y) + " " + Arrays.equals(x, y) + " " + Arrays.deepEquals(x, y));
        System.out.println("hello".substring(1, 4).length());
        System.out.println("a.b".split(".").length + " " + "a.b".split("\\.").length);
    }
}
```

```output
java
false true
false false true
3
0 2
```

`Arrays.equals` on a nested array compares the inner arrays with `equals` -
that is, by reference - which is why only `deepEquals` says `true`. The
other lines: `toUpperCase()` returned a new string that nobody kept, so `s`
is still `java`; the runtime-built string is a different object with the same
characters; `substring(1, 4)` is positions 1, 2 and 3, so 3 characters; and
splitting on the regex `.` leaves nothing but empty strings, which `split`
drops, while `\\.` splits on the real dot.

## Your turn

In `Paper2.java`:

- `public static String chained(String s)` — trimmed, spaces replaced with
  underscores, uppercased, in that order: `"  hello world "` gives
  `"HELLO_WORLD"`
- `public static boolean identical(String a, String b)` — are they the same
  object? (This one really should use `==`: it is the question being asked.)
- `public static boolean equivalent(String a, String b)` — do they hold the
  same characters?
- `public static boolean sameElements(int[] a, int[] b)` — element by element,
  so arrays of different lengths, or the same numbers in a different order,
  are not the same
- `public static String describe(int[] values)` — `"[1, 2, 3] len=3"`, and
  `"[] len=0"` for an empty array
- `public static String middle(String s)` — the middle third of a string whose
  length divides by three: `"123456"` is split into `"12"`, `"34"` and `"56"`,
  so the answer is `"34"`; for `"abc"` it is `"b"`. With a third `n` long, the
  middle runs from position `n` up to (not including) `2 * n`.
