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

## Your turn

In `Paper2.java`:

- `public static String chained(String s)` — trimmed, spaces replaced with
  underscores, uppercased
- `public static boolean identical(String a, String b)` — are they the same
  object?
- `public static boolean equivalent(String a, String b)` — do they hold the
  same characters?
- `public static boolean sameElements(int[] a, int[] b)` — element by element
- `public static String describe(int[] values)` — `"[1, 2, 3] len=3"`
- `public static String middle(String s)` — the middle third of a string whose
  length divides by three
