---
title: javac, java and the classpath
summary: What the JDK actually does to your source, why a class must match its filename, and where the compiler looks for everything else.
order: 1
files: [Greeter.java]
run: javac Greeter.java && java Greeter
hints:
  - "The file is Greeter.java, so the public class in it must be called exactly `Greeter` - the compiler enforces the match."
  - "`greet(String name)` returns a String; it does not print. Returning is what makes it testable, and printing inside a method you want to test is the first habit to unlearn."
  - "`main` has a fixed signature: `public static void main(String[] args)`. Any deviation compiles fine and simply is not the entry point."
  - "Use `String.format(\"Hello, %s!\", name)` or plain concatenation - either is fine here."
---

Java is compiled, then run, and the two steps use different tools. Most early
confusion comes from not knowing which one is complaining.

```bash
javac Greeter.java     # source  -> Greeter.class  (bytecode)
java Greeter           # run the class, by NAME, not by filename
```

Notice the asymmetry: `javac` takes a **file**, `java` takes a **class name**.
`java Greeter.class` is a common first error and does not work.

## The filename rule

A public class must live in a file with exactly its own name. `class Greeter`
must be in `Greeter.java` — not `greeter.java`, not `Main.java`. The compiler
enforces it, and the error is blunt:

```
class Greeter is public, should be declared in a file named Greeter.java
```

This rule exists so the compiler can find a class from its name without
scanning every file, which is the same reason packages map to directories.

## main

```java
public static void main(String[] args)
```

Every word is required. `public` so the launcher can call it, `static` so it
runs without an instance, `void` because there is nothing to return to, and an
array of strings for the arguments. Change any of it and the class still
compiles — it just is not an entry point, and you get "Main method not found".

`String... args` is also accepted, because varargs *are* an array.

## The classpath

The classpath is where Java looks for classes. It defaults to the current
directory, which is why the examples above work with no flags.

```bash
javac -cp lib/junit.jar:. Greeter.java
java -cp . Greeter
```

Entries are separated by `:` on Linux and `;` on Windows. When Java says
`NoClassDefFoundError`, it compiled fine and cannot find the class **now** —
which is a classpath problem, not a code problem. `ClassNotFoundException` is
the same idea from a reflective lookup.

## JDK, JRE, JVM

| | |
|---|---|
| **JVM** | runs bytecode |
| **JRE** | the JVM plus the standard library — enough to *run* |
| **JDK** | the JRE plus `javac` and the tools — enough to *build* |

You have a JDK here: `java -version` and `javac -version` both answer.

## Your turn

In `Greeter.java`:

- a public class `Greeter`
- `public static String greet(String name)` returning `Hello, <name>!`
- `public static void main(String[] args)` that prints the result of
  `greet("world")`

Run it yourself with `javac Greeter.java && java Greeter`.
