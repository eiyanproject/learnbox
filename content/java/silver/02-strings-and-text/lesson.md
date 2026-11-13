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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **`String`** | Java's class for text |
| **immutable** | can never change once created; `String` methods return new strings |
| **mutable** | can be changed in place, like a `StringBuilder` |
| **reference** | the address of an object; a `String` variable holds one |
| **same object** vs **same content** | `==` asks the first; `equals` asks the second |
| **string pool** | the one shared copy of each string literal in the code |
| **interning** | putting a string in the pool |
| **run time** | while the program runs; strings built then are new objects, not pooled |
| **position** (index) | where a character is, counting from 0 |
| **exclusive end** | `substring(a, b)` stops before `b`; the result has `b - a` characters |
| **whitespace** | spaces, tabs and newlines |
| **Unicode** | the standard that numbers every character in every language |
| **CSV** | comma-separated values: one record per line, fields split by commas |
| **regex** (regular expression) | a pattern language; `split` takes one |
| **escape** | a backslash that makes the next character literal; in a Java string `\\` is one backslash |
| **buffer** | the changeable storage inside a `StringBuilder` |
| **chaining** | calling a method on what the previous call returned: `sb.append("a").append("b")` |
| **return-this** | a method that changes the object and returns that same object |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Text.java && java Text` | builds and runs this lesson's file |

### Java classes and methods

| Name | What it does |
|---|---|
| `s.length()` | number of characters (a method: brackets; arrays use the field `length`) |
| `s.charAt(i)` | the character at position `i`, as a `char` |
| `s.substring(a, b)` | the characters from `a` up to, not including, `b` |
| `s.indexOf(t)` | where `t` first appears, or -1 |
| `s.trim()`, `s.strip()` | a copy without spaces at the ends; `strip` knows Unicode spaces |
| `s.toUpperCase()`, `s.toLowerCase()` | a copy in capitals or small letters |
| `s.replace(a, b)` | a copy with every `a` replaced by `b` |
| `s.split(regex)` | the pieces between matches of the pattern, as a `String[]` |
| `split("\\.")`, `split("\\s+")` | split on a real full stop; on any run of whitespace |
| `s.isBlank()` | `true` if empty or only whitespace |
| `a.equals(b)`, `a.equalsIgnoreCase(b)` | same text; same text ignoring capitals |
| `new String("java")` | a new string object, not the pooled one |
| `Integer.parseInt("1815")` | text to an `int` |
| `String.join(".", parts)` | joins pieces with a separator |
| `new StringBuilder()`, `new StringBuilder(s)` | an empty builder; one starting with `s` |
| `sb.append(x)`, `insert`, `delete`, `reverse()` | change the builder and return it |
| `sb.toString()` | the builder's contents as an ordinary `String` |
| `s += i` | builds a whole new string each time; slow in a loop |

### Errors

| Error | Means |
|---|---|
| `StringIndexOutOfBoundsException` | a position outside the string, as in `"hello".substring(1, 9)` |
| *(no error at all)* | `s.trim();` with the result thrown away: it compiles and does nothing |

---

Text is everywhere in programs, and Java's `String` class handles it. It
behaves differently from strings in some other languages in two ways that
matter: a `String` can never change, and `==` does not compare the text. Both
cause bugs that compile and run without any error, which is why the exam
returns to them again and again.

A `String` in Java is **immutable**: once created, its characters can never
change. Nothing you call on it changes it — every method that looks like it
modifies a string actually returns a new one, and leaves the original as it
was.

```java
String s = "  hello ";
s.trim();                 // does nothing you can observe
s = s.trim();             // this is what you meant
```

(A fragment.) That first line compiles, runs, and has no effect: `trim()` builds a new,
trimmed string and returns it, and since nothing stores the result, it is
thrown away. The second line stores the new string back in `s`. It is the
single most common Java beginner bug and it appears on the exam in disguise
almost every time.

Immutability is deliberate. A string can be shared freely, between variables,
threads, or as a key in a map, because nobody holding it can change it under
anyone else's feet.

## == compares references

A `String` variable holds a **reference**, the address of a string object,
not the characters themselves. `==` on two references asks "are these the very
same object?", not "do they hold the same text?". For the text, use
`equals`:

```java
String a = "java";
String b = "java";
String c = new String("java");

a == b        // true  - both point at the same pooled literal
a == c        // false - c is a different object
a.equals(c)   // true  - same characters
```

(Expressions with their results; the full program at the end of the lesson
prints them.)

Java keeps one shared copy of each string literal, in what is called the
**string pool**, and every `"java"` written in the code refers to that one
object. Putting a string in the pool is called **interning** it. So `==`
*appears* to work until the string comes from input, concatenation at
runtime, or `new`. Then it fails, and the bug is intermittent in the worst
way. **Use `equals` for content, always.** (`equalsIgnoreCase` compares
ignoring capitals.)

## The methods worth knowing

| Method | |
|---|---|
| `length()` | the number of characters. A method, so it has brackets; arrays use the field `length`, with none |
| `charAt(i)` | one character, as a `char`; positions start at 0 |
| `substring(a, b)` | from a, **up to but not including** b |
| `indexOf(s)` | position, or -1 |
| `trim()` / `strip()` | remove spaces from both ends; `strip` also understands Unicode spaces, so prefer it |
| `toUpperCase()` / `toLowerCase()` | a copy in upper or lower case |
| `replace(a, b)` | all occurrences |
| `split(regex)` | note it takes a **regex**, not a literal |
| `isBlank()` | empty or only whitespace |

`substring` being exclusive at the end means `"hello".substring(1, 3)` is
`"el"`: positions 1 and 2. The length of the result is `b - a`, which is the
easy way to remember it. A position past the end is not forgiven, as it is
in Python: `"hello".substring(1, 9)` throws `StringIndexOutOfBoundsException`.

The everyday use of `split` is data in a fixed format, such as one line of a
CSV (comma-separated values) file, the format spreadsheets export:

```java
public class Csv {
    public static void main(String[] args) {
        String line = "ada,1815,London";
        String[] parts = line.split(",");
        System.out.println(parts.length);               // prints 3
        System.out.println(parts[0] + " was born in " + parts[1]);
        int born = Integer.parseInt(parts[1]);          // text to a number
        System.out.println(2026 - born);                // prints 211
    }
}
```

```output
3
ada was born in 1815
211
```

`split` returns an array of the pieces (arrays are the lesson after next;
`parts[0]` is the first piece). Every piece is a `String`, even `"1815"`, so
arithmetic needs `Integer.parseInt` first.

A **regex** (regular expression) is a pattern language in which some
characters have special meanings. `split(",")` is safe, because a comma means
itself, but a `.` means "any character", so splitting on a literal full stop
needs `split("\\.")`: the backslash says "a real full stop", and it is doubled
because a backslash inside a Java string must itself be escaped. To split on
any run of spaces, use `split("\\s+")`, where `\s` is "a whitespace character"
and `+` is "one or more".

## StringBuilder

Because a `String` cannot change, `s += i` cannot add to `s`. It builds a
whole new string, copying every character so far plus the new ones, and
points `s` at it. In a loop that means a new String every iteration, each one
longer than the last:

```java
String s = "";
for (int i = 0; i < 10000; i++) s += i;    // 10000 discarded objects
```

(A fragment: both of these belong inside a method.) The work grows with the
square of the length, so it gets slow fast. `StringBuilder` is a mutable
sequence of characters, built for exactly this; it mutates one buffer
instead:

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) sb.append(i);
String s = sb.toString();
```

`toString()` at the end turns the builder's contents into an ordinary,
immutable `String`.

Its methods — `append`, `insert`, `delete`, `reverse` — change the builder and
return it, which is why they chain: `sb.append("a").append("b")` calls the
second `append` on the same builder the first one returned. That
return-**this** behaviour is the opposite of String's return-a-copy, and the
exam contrasts them deliberately. Calling `sb.reverse();` without using the
result still reverses `sb`, which is exactly the line that does nothing for a
`String`.

Concatenating a few pieces in one expression, `"Hello, " + name + "!"`, is
fine: the compiler turns it into efficient code itself. The loop is the case
to avoid.

## The traps, run

Each line of this program is an exam question. Cover the output and predict
all seven lines first:

```java
public class Strings {
    public static void main(String[] args) {
        String s = "  hello ";
        s.trim();
        System.out.println("[" + s + "]");
        s = s.trim();
        System.out.println("[" + s + "]");

        String a = "java", b = "java", c = new String("java");
        System.out.println((a == b) + " " + (a == c) + " " + a.equals(c));
        String half = "ja";
        String built = half + "va";                  // made at run time
        System.out.println((a == built) + " " + a.equals(built));

        System.out.println("hello".substring(1, 3));
        System.out.println("a.b.c".split(".").length + " " + "a.b.c".split("\\.").length);

        StringBuilder sb = new StringBuilder("abc");
        sb.append("d").reverse();                    // changes sb itself
        System.out.println(sb);
    }
}
```

```output
[  hello ]
[hello]
true false true
false true
el
0 3
dcba
```

Going through it: the first `trim()` result was thrown away, so the
brackets show the original spaces. The pooled literals `a` and `b` are the
same object, `c` and `built` are not, and `equals` is true for all of them.
`substring(1, 3)` is positions 1 and 2. And `reverse()` changed `sb` itself.

`split(".")` gives **zero** parts: `.` is the regex for "any character", so
every character is a separator and only empty strings are left, which `split`
then drops (it always drops empty strings at the end of the result).
`split("\\.")` splits on real full stops and gives the three parts.

## Your turn

In `Text.java`:

- `public static String shout(String s)` — trimmed, uppercased, with `!`
  added: `shout("  hello ")` is `"HELLO!"`
- `public static String reverse(String s)` — the characters in reverse
  order, using StringBuilder: `reverse("java")` is `"avaj"`, and the empty
  string stays empty
- `public static boolean sameContent(String a, String b)` — whether the two
  hold the same text. A test passes in a string built at run time, so `==`
  gives the wrong answer there.
- `public static String initials(String fullName)` — the first letter of each
  name, upper-cased, each followed by a full stop: `"ada lovelace"` becomes
  `"A.L."`. Extra spaces anywhere make no difference:
  `"  grace   hopper "` becomes `"G.H."` (trim first, then split on runs of
  spaces).
