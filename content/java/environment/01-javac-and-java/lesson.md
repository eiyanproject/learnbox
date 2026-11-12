---
title: javac, java and the classpath
summary: What the JDK actually does to your source, why a class must match its filename, and where the compiler looks for everything else.
order: 1
files: [Greeter.java]
run: javac Greeter.java && java Greeter
hints:
  - "The file is Greeter.java, so the public class in it must be called exactly `Greeter` - the compiler enforces the match."
  - "`greet(String name)` returns a String; it does not print. Returning is what makes it testable, and printing inside a method you want to test is the first habit to unlearn."
  - "`main` has a fixed signature: `public static void main(String[] args)`. On this box's Java 21, any deviation compiles fine and simply is not the entry point."
  - "Use `String.format(\"Hello, %s!\", name)` or plain concatenation - either is fine here."
---

In Python or JavaScript, you run the source file directly. Java adds a step:
your source is first **compiled**, translated by a program called the
**compiler** into a compact form the machine can run quickly, and only then
**run**. The two steps use different tools, and they fail in different ways.
Most early confusion comes from not knowing which one is complaining, so this
lesson takes them one at a time.

```bash
javac Greeter.java     # source  -> Greeter.class  (bytecode)
java Greeter           # run the class, by NAME, not by filename
```

(In command examples like this, type the command itself; the `#` and
everything after it is a comment for you to read. When a command is shown
with a leading `$`, do not type the `$` either: it stands for the terminal's
prompt.)

- `javac` (Java compiler) reads `Greeter.java` and, if the code is valid,
  writes `Greeter.class`. That file holds **bytecode**: instructions for the
  Java Virtual Machine rather than for any particular processor, which is why
  the same `.class` file runs on Linux, macOS and Windows.
- `java` starts the **Java Virtual Machine** (JVM), loads the class you name,
  and runs its `main` method.

Notice the asymmetry: `javac` takes a **file**, `java` takes a **class name**.
`java Greeter.class` is a common first error and does not work: the launcher
looks for a class literally called `Greeter.class`, finds none, and says so:

```text
$ java Greeter.class
Error: Could not find or load main class Greeter.class
Caused by: java.lang.ClassNotFoundException: Greeter.class
```

Since Java 11 there is also a shortcut for single-file programs:
`java Greeter.java` compiles the file in memory and runs it straight away,
without leaving a `.class` file behind. It is handy for quick experiments; the
two-step form is what real projects, and this lesson's tests, use.

### Which tool is complaining?

- A message from `javac` that starts with `Greeter.java:3: error:` is a
  **compile-time** error. Nothing ran; the file was not valid Java, and no
  `.class` file was written (or the old one was left as it was).
- A message from `java` such as `Exception in thread "main" ...` is a
  **run-time** error. The code compiled, started, and failed while running.
- A message from `java` starting `Error: Could not find or load main class`
  means the launcher could not even start: wrong class name, or the class is
  not on the classpath (below).

### Reading a stack trace

A run-time error prints a **stack trace**: the error, then the chain of
method calls that led to it, most recent first. This version of `Greeter` has
a bug: it takes the first letter of a name without checking that there is
one.

```java
public class Greeter {
    static String initial(String name) {
        return name.substring(0, 1);
    }

    static String greet(String name) {
        return "Hello, " + initial(name) + "!";
    }

    public static void main(String[] args) {
        System.out.println(greet("Ada"));
        System.out.println(greet(""));
    }
}
```

Before reading on, predict what happens on the second `greet`. Here is the
run, with nine lines from inside the JDK cut down to one:

```text
$ java Greeter
Hello, A!
Exception in thread "main" java.lang.StringIndexOutOfBoundsException: Range [0, 1) out of bounds for length 0
	at java.base/jdk.internal.util.Preconditions$1.apply(Preconditions.java:55)
	... (eight more lines starting java.base/)
	at Greeter.initial(Greeter.java:3)
	at Greeter.greet(Greeter.java:7)
	at Greeter.main(Greeter.java:12)
```

How to read it:

1. **The first line** names the exception and says what went wrong: asking
   for characters 0 to 1 of a string of length 0.
2. **Skip the lines starting `java.base/`.** They are inside the JDK's own
   code. The bug is almost never there; it is in what your code asked for.
   (Exactly which internal lines appear depends on the Java version.)
3. **The first line in your own file** is where it failed:
   `Greeter.initial(Greeter.java:3)`, the method `initial`, line 3 of
   `Greeter.java`, which is the `substring` call.
4. **Read downwards for how you got there:** `initial` was called by `greet`
   on line 7, which was called by `main` on line 12, the `greet("")` call.

The fix belongs where the bad value came from or where it should have been
checked, not necessarily on the line that threw. Here `initial` should
handle an empty name.

Breaking a working program on purpose, by deleting a semicolon or passing an
empty string, and reading what Java says is one of the fastest ways to learn
the messages before you meet them for real.

### Trying things out in jshell

The JDK includes **`jshell`**, an interactive prompt that runs Java one line
at a time, with no class and no `main`. It is the quickest way to check how
something behaves before you rely on it:

```text
$ jshell
jshell> Integer.MAX_VALUE
$1 ==> 2147483647
jshell> 7 / 2
$2 ==> 3
jshell> "Greeter".length()
$3 ==> 7
jshell> /exit
```

Each result is shown after `==>`; `$1`, `$2` and so on are names `jshell`
gives the results so you can use them again. Type `/exit` (or press Ctrl+D)
to leave. It is in this lesson's terminal; use it whenever a lesson says
"try it".

## The filename rule

A public class must live in a file with exactly its own name. `class Greeter`
must be in `Greeter.java` — not `greeter.java`, not `Main.java`. The compiler
enforces it, and the error is blunt:

```text
$ javac Main.java
Main.java:1: error: class Greeter is public, should be declared in a file named Greeter.java
public class Greeter {
       ^
1 error
```

The caret `^` under the line points at the exact spot the compiler objects
to, here the class name. Capital letters count: Linux file names are
case-sensitive, so `greeter.java` is a different name.

This rule exists so the compiler can find a class from its name without
scanning every file, which is the same reason packages map to directories
(next lesson). A file can hold other, non-public classes as well, but at most
one public one.

## main

```java
public static void main(String[] args)
```

`main` is the **entry point**: the method the launcher calls to start the
program. Every word is required:

- `public` so the launcher, which lives outside your class, is allowed to
  call it;
- `static` so it runs without an instance: nothing has created a `Greeter`
  object yet when the program starts;
- `void` because there is nothing to return to; a program's exit status is
  set with `System.exit(code)` instead;
- `String[] args`, an array of strings holding whatever was typed after the
  class name on the command line: `java Greeter Ada Bo` gives
  `args[0]` = `"Ada"` and `args[1]` = `"Bo"`.

Change any of it and the class still compiles — `javac` has no opinion about
which method you intend to start from — but it is not an entry point, and
the launcher refuses to start:

```text
$ java Greeter
Error: Main method not found in class Greeter, please define the main method as:
   public static void main(String[] args)
```

`String... args` is also accepted, because varargs *are* an array.

A version note. That strict rule is what Java 21, on this box, enforces,
and it is what the certification exams test. Java 25 relaxed it: from there on,
`main` may leave out `public`, `static` and even the `args` parameter. Older
code and the exam use the full form, so learn that one.

## The classpath

When your code uses another class, both the compiler and the JVM have to find
that class's `.class` file. The **classpath** is the list of places they look:
folders, and `.jar` files (a **jar** is a zip archive of `.class` files, the
usual way libraries are shipped). It defaults to the current directory, which
is why the examples above work with no flags.

```bash
javac -cp lib/junit.jar:. Greeter.java
java -cp . Greeter
```

`-cp` (short for `-classpath`) replaces the default. The first line compiles
with two places to look: the JUnit library jar and `.`, the current
directory. Leave out the `.` and your own classes in the current directory
are no longer found.

Entries are separated by `:` on Linux and macOS and by `;` on Windows. When
Java says `NoClassDefFoundError`, it compiled fine and cannot find the class
**now** — which is a classpath problem, not a code problem:

```text
$ java Uses
Exception in thread "main" java.lang.NoClassDefFoundError: Helper
	at Uses.main(Uses.java:2)
Caused by: java.lang.ClassNotFoundException: Helper
```

Here `Uses` was compiled while `Helper.class` existed, and then `Helper.class`
was deleted. The code is fine; the class is simply not where the JVM looks.
`ClassNotFoundException` is the same idea from a **reflective** lookup, where
code asks for a class by its name as a string, such as
`Class.forName("Helper")`.

## JDK, JRE, JVM

| | |
|---|---|
| **JVM** | runs bytecode |
| **JRE** | the JVM plus the standard library — enough to *run* |
| **JDK** | the JRE plus `javac` and the tools — enough to *build* |

Each one contains the one above it. The **standard library** is the large
collection of ready-made classes every Java program can use, such as `String`,
`List` and `Files`. The JRE used to be downloadable on its own, for machines
that only run Java programs; modern Java distributions ship only the JDK.

You have a JDK here: `java -version` and `javac -version` both answer.

## Your turn

In `Greeter.java`:

- a public class `Greeter`
- `public static String greet(String name)`, which **returns** (not prints)
  `Hello, <name>!`: `greet("Ada")` is `"Hello, Ada!"`, and `greet("")` is
  `"Hello, !"`
- `public static void main(String[] args)` that prints the result of
  `greet("world")`

The tests call `greet` directly and compare what it returns, which is only
possible because it returns a value instead of printing one. They also check
`main`'s signature, so write all four words.

Run it yourself with `javac Greeter.java && java Greeter` (the **Run**
button does exactly that; `&&` runs the second command only if the first
succeeded).
