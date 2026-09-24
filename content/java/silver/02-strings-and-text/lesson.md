---
title: Strings, immutability and StringBuilder
summary: Why every String method returns a new String, when == is not what you want, and the one place mutation belongs.
order: 2
files: [Text.java]
run: javac Text.java && java Text
hints:
  - "`shout` should trim, uppercase and add an exclamation mark. Each String method RETURNS a new String - calling s.trim() without using the result does nothing."
  - "`reverse` is what StringBuilder is for: `new StringBuilder(s).reverse().toString()`."
  - "`sameContent` must use `.equals()`, not `==`. The test deliberately builds a String at runtime so the two are not the same object."
  - "`initials`: split on a space, take charAt(0) of each part, uppercase it, and join. `String.join` or a StringBuilder both work."
---

A `String` in Java is immutable. Nothing you call on it changes it — every
method that looks like it modifies a string actually returns a new one.

```java
String s = "  hello ";
s.trim();                 // does nothing you can observe
s = s.trim();             // this is what you meant
```

That first line compiles, runs, and has no effect. It is the single most common
Java beginner bug and it appears on the exam in disguise almost every time.

## == compares references

```java
String a = "java";
String b = "java";
String c = new String("java");

a == b        // true  - both point at the same pooled literal
a == c        // false - c is a different object
a.equals(c)   // true  - same characters
```

Literals are interned into a shared pool, so `==` *appears* to work until the
string comes from input, concatenation at runtime, or `new`. Then it fails, and
the bug is intermittent in the worst way. **Use `equals` for content, always.**

## The methods worth knowing

| Method | |
|---|---|
| `length()` | no parentheses on arrays — `length` there, `length()` here |
| `charAt(i)` | one character |
| `substring(a, b)` | from a, **up to but not including** b |
| `indexOf(s)` | position, or -1 |
| `trim()` / `strip()` | strip is Unicode-aware; prefer it |
| `replace(a, b)` | all occurrences |
| `split(regex)` | note it takes a **regex**, not a literal |
| `isBlank()` | empty or only whitespace |

`substring` being exclusive at the end means `"hello".substring(1, 3)` is
`"el"` — length is `b - a`, which is the easy way to remember it.

## StringBuilder

Concatenating in a loop creates a new String every iteration:

```java
String s = "";
for (int i = 0; i < 10000; i++) s += i;    // 10000 discarded objects
```

`StringBuilder` mutates one buffer instead:

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) sb.append(i);
String s = sb.toString();
```

Its methods — `append`, `insert`, `delete`, `reverse` — change the builder and
return it, which is why they chain. That return-**this** behaviour is the
opposite of String's return-a-copy, and the exam contrasts them deliberately.

## Your turn

In `Text.java`:

- `public static String shout(String s)` — trimmed, uppercased, with `!`
- `public static String reverse(String s)` — using StringBuilder
- `public static boolean sameContent(String a, String b)` — content comparison
- `public static String initials(String fullName)` — `"ada lovelace"` becomes
  `"A.L."`
