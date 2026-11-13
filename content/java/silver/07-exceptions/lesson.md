---
title: Exceptions, finally and try-with-resources
summary: Checked against unchecked, the order of catch blocks, what finally really guarantees, and the construct that replaced it.
order: 7
files: [Safe.java]
run: javac Safe.java && java Safe
hints:
  - "`parseOrDefault` catches NumberFormatException - which is unchecked, so nothing forces you to catch it, but catching it here is the point."
  - "`divide` should throw ArithmeticException for a zero divisor. Integer division by zero already throws it, so letting it happen is a legitimate answer."
  - "`describe` must catch the more specific exception FIRST: a catch for Exception above one for IllegalArgumentException does not compile."
  - "`closeOrder` uses try-with-resources with two resources - they are closed in REVERSE order of declaration, which is what the test checks."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **exception** | an object describing a problem, thrown where the problem happens |
| **throw** | stop the method and send the exception back up the calls |
| **catch** | handle an exception so the program carries on |
| **propagate** | an uncaught exception travelling on to the caller |
| **stack trace** | the exception plus the calls that led to it, printed if nothing catches it |
| **`Throwable`** | the root of every exception class |
| **`Error`** | a problem with the JVM itself, such as running out of memory; do not catch |
| **checked exception** | under `Exception` but not `RuntimeException`; must be caught or declared |
| **unchecked exception** | under `RuntimeException` (or `Error`); the compiler does not insist |
| **declare** (`throws`) | list a checked exception in a method's header, warning every caller |
| **compile-time** vs **run-time** | caught by `javac` vs seen only when the line runs |
| **`try` block** | the code that might throw |
| **`catch` block** | runs if a matching exception is thrown; tried in order, first match wins |
| **unreachable catch** | a narrower catch placed after a broader one; a compile error |
| **multi-catch** | one `catch` for several unrelated types: `A \| B e` |
| **effectively final** | never reassigned, even without the word `final` |
| **`finally`** | runs last in every case: after success, after a catch, even after `return` |
| **resource** | something from the operating system (a file, a connection) that must be closed |
| **try-with-resources** | `try (...)`: resources declared there are closed automatically |
| **`AutoCloseable`** | the interface with `close()`; anything implementing it can go in `try (...)` |
| **reverse order** | resources close last-opened first |
| **suppressed exception** | one thrown by `close()` while another was already in flight; attached to it |
| **record** | a compact class that just holds values (Silver lesson 8) |
| **`Runnable`** | an interface for "code to run", with one method `run()` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `java Age.java` | runs a single-file program without a separate `javac` step |
| `javac Safe.java && java Safe` | builds and runs this lesson's file |

### Java keywords, classes and methods

| Name | What it does |
|---|---|
| `try { } catch (NumberFormatException e) { } finally { }` | the full form |
| `catch (NumberFormatException \| ArithmeticException e)` | multi-catch |
| `String firstLine(Path file) throws IOException` | declares a checked exception |
| `throw new RuntimeException("lost");` | throws an exception |
| `e.getMessage()` | the exception's message |
| `e.getSuppressed()` | exceptions suppressed while closing resources |
| `try (Scanner in = ...; PrintWriter out = ...) { }` | try-with-resources with two resources |
| `public void close()` | the method `AutoCloseable` requires |
| `Integer.parseInt(s)` | text to `int`; throws `NumberFormatException` |
| `Files.readAllLines(file)` | reads a file's lines; can throw `IOException` |
| `action.run()` | runs a `Runnable` |
| `@SuppressWarnings("finally")` | silences the compiler's warning about returning from `finally` |
| `System.exit()` | ends the program; the one way to skip `finally` |

### Errors

| Error | Means |
|---|---|
| `NumberFormatException` | text that is not a number, such as `"forty"`; a kind of `IllegalArgumentException` |
| `ArithmeticException` | integer division by zero |
| `IllegalArgumentException` | an argument that makes no sense |
| `IllegalStateException` | the object is not in a state where the call makes sense |
| `NullPointerException` | used a reference that is `null` |
| `IOException`, `FileNotFoundException` | checked: an input/output problem; a missing file (a subclass) |
| `SQLException` | checked: a database problem |
| `OutOfMemoryError`, `StackOverflowError` | the JVM ran out of memory; calls went too deep |
| `unreported exception IOException; must be caught or declared to be thrown` | a checked exception neither caught nor declared |
| `exception FileNotFoundException has already been caught` | a narrower catch after a broader one |

---

A method that cannot do its job, because a file is missing, a number will not
parse, or an argument makes no sense, needs a way to say so that the caller
cannot simply overlook. Java's answer is the **exception**: an object
describing the problem, **thrown** at the point of failure. Throwing stops the
method there, and the exception travels back up through the calls until some
code **catches** it. If none does, the program stops and prints a **stack
trace**, the list of method calls that led to the failure.

Java is unusual in letting the compiler check some of this, which is what the
"checked" in checked exceptions means. This lesson covers which exceptions
are checked, the rules for catching them, and the guarantees `finally` and
try-with-resources make about clean-up.

## The hierarchy

Every exception is an object of a class under `Throwable`, and the position
in this tree decides the rules:

```text
Throwable
 ├── Error                    (OutOfMemoryError, StackOverflowError - do not catch)
 └── Exception
      ├── RuntimeException    unchecked: NullPointer, IllegalArgument, Arithmetic...
      └── everything else     checked: IOException, SQLException...
```

**Checked** exceptions must be caught or declared with `throws`; the compiler
enforces it. **Unchecked** ones — anything under `RuntimeException`, plus
`Error` — need neither.

"Declared" means written in the method's header, which warns every caller:

```java
String firstLine(Path file) throws IOException {   // callers must deal with it
    return Files.readAllLines(file).get(0);
}
```

(A sketch of one method.) `Files.readAllLines` can throw the checked
`IOException`. `firstLine` does not catch it, so it must list it after
`throws`, and every method that calls `firstLine` then faces the same choice:
catch it, or declare it too. Leave out both and the code does not compile:

```text
error: unreported exception IOException; must be caught or declared to be thrown
```

That is a **compile-time** error. Unchecked exceptions, by contrast, only
ever show up at **run time**, when the bad line actually executes.

The division is about intent: checked means "this can fail for reasons outside
your control, deal with it"; unchecked means "this is a bug, fix the code". A
missing file is not the programmer's fault, so `IOException` is checked; a
`null` passed where an object was required is, so `NullPointerException` is
not. `Error`s, such as running out of memory, are problems with the JVM itself
that a program cannot sensibly recover from.

## try, catch, finally

First, what happens with no handling at all. This program reads an age that
is not a number:

```text
$ java Age.java
Exception in thread "main" java.lang.NumberFormatException: For input string: "forty"
	at java.base/java.lang.NumberFormatException.forInputString(NumberFormatException.java:67)
	at java.base/java.lang.Integer.parseInt(Integer.java:529)
	...
	at Age.main(Age.java:3)
```

The exception was thrown inside `parseInt`, nothing caught it, so the
program stopped there and printed a stack trace (Environment lesson 1 shows
how to read one). The line after it, printing "next year", never ran.

Wrapping the risky call in `try` and saying what to do in `catch` lets the
program carry on. A print placed after the risky line, inside the `try`,
shows exactly what is skipped:

```java
public class Age {
    static void read(String text) {
        try {
            int age = Integer.parseInt(text);
            System.out.println("parsed " + age);      // skipped if parseInt throws
        } catch (NumberFormatException e) {
            System.out.println("not a number: " + e.getMessage());
        }
        System.out.println("carrying on");
    }

    public static void main(String[] args) {
        read("41");
        read("forty");
    }
}
```

```output
parsed 41
carrying on
not a number: For input string: "forty"
carrying on
```

With `"41"` the whole `try` block ran and the `catch` was skipped. With
`"forty"`, `parseInt` threw, the rest of the `try` block (the "parsed" line)
was skipped, the `catch` ran, and then the program carried on after the whole
statement either way.

The full form has several catches and a `finally`:

```java
try {
    risky();
} catch (FileNotFoundException e) {   // most specific first
    ...
} catch (IOException e) {
    ...
} finally {
    cleanup();                        // runs either way
}
```

(A sketch: `...` stands for handling code.) The steps:

1. The `try` block runs.
2. If it throws, the rest of the `try` block is skipped, and Java checks the
   `catch` blocks from the top. The first one whose type matches the
   exception (the same class or a parent of it) runs, and only that one.
3. If no `catch` matches, the exception carries on up to the caller.
4. `finally`, if present, runs last in every case: after a normal finish,
   after a `catch`, and even when the exception is not caught at all.

Inside a `catch`, `e` is the exception object; `e.getMessage()` is its
message.

Catch blocks are tried **in order**, and a broader type above a narrower one is
a compile error — unreachable code. `FileNotFoundException` is a subclass of
`IOException`, so a `catch (IOException e)` placed first would catch every
`FileNotFoundException` too, and the block after it could never run:

```text
error: exception FileNotFoundException has already been caught
```

This is checked at compile time, which makes it a reliable exam question.

Multi-catch handles unrelated types together:

```java
catch (NumberFormatException | ArithmeticException e)
```

The variable is effectively final there (it cannot be reassigned), and the
types may not overlap: listing a class together with its own parent is a
compile error, since the parent alone would already cover both.

## What finally guarantees

`finally` runs whether or not an exception was thrown, **and even if the try
block returns**. A `return` inside `finally` replaces the one from `try`,
discarding the original — and discarding any in-flight exception with it, which
is why it is considered a mistake rather than a technique. (The one way to
skip `finally` is to end the whole program, with `System.exit()`, before it
runs.) `f()` and `g()` in the program below show both cases.

## try-with-resources

```java
try (Scanner in = new Scanner(file); PrintWriter out = new PrintWriter(dest)) {
    ...
}
```

(A sketch: `file` and `dest` stand for real files.) Files, network
connections and database connections are **resources**: they hold something
from the operating system that must be handed back by calling `close()`, even
when the code using them fails. The objects created in the brackets after
`try` are closed for you when the block ends, however it ends.

Anything implementing `AutoCloseable` (an interface with one method,
`close()`) is closed automatically, **in reverse order of declaration**,
before any catch or finally runs. Reverse order is deliberate: `out` was
opened last and may depend on `in`, so it is closed first. Resources are
implicitly final. This is strictly better than closing in `finally`, where an
exception during close can mask the real one — here the close exception is
*suppressed* and attached to the original, retrievable with
`getSuppressed()`. You see the real failure, not a secondary one.

## The order, printed

```java
public class Finally {
    static int f() {
        try {
            return 1;
        } finally {
            System.out.println("finally runs before the return completes");
        }
    }

    @SuppressWarnings("finally")
    static int g() {
        try {
            throw new RuntimeException("lost");
        } finally {
            return 2;                       // the exception is discarded
        }
    }

    record Res(String name) implements AutoCloseable {
        public void close() { System.out.println("close " + name); }
    }

    public static void main(String[] args) {
        System.out.println(f());
        System.out.println(g());
        try (Res a = new Res("a"); Res b = new Res("b")) {
            System.out.println("body");
            throw new IllegalStateException("boom");
        } catch (IllegalStateException e) {
            System.out.println("catch " + e.getMessage());
        } finally {
            System.out.println("finally");
        }
    }
}
```

```output
finally runs before the return completes
1
2
body
close b
close a
catch boom
finally
```

Following it through:

- `f()` reaches `return 1`, but before the method actually returns, `finally`
  runs and prints its line. Then the 1 comes back and is printed.
- `g()` throws, `finally` runs, and its `return 2` replaces the exception
  entirely: `"lost"` is never seen. The `@SuppressWarnings("finally")` above
  it silences the compiler's warning about exactly this.
- In the `try`-with-resources, the body prints, then throws. Before the
  `catch` runs, both resources are closed, `b` first because it was declared
  last. Then the `catch` handles the exception, and `finally` runs last.

`record Res(String name)` is a compact way of declaring a small class that
holds a `name` (records are covered in the next lesson); here it is the
simplest possible `AutoCloseable`.

## Your turn

In `Safe.java`:

- `public static int parseOrDefault(String s, int fallback)` — the parsed int
  (`Integer.parseInt(s)`), or the fallback if it will not parse. `"twelve"`,
  the empty string and `null` all give the fallback: `parseInt` throws
  `NumberFormatException` for each of them.
- `public static int divide(int a, int b)` — `a / b` with integer division
  (`divide(7, 2)` is 3); throws `ArithmeticException` when `b` is zero
- `public static String describe(Runnable action)` — runs it (`action.run()`)
  and returns `"ok"` if nothing is thrown, `"bad argument"` for an
  `IllegalArgumentException`, or `"failed"` for any other exception. A
  `Runnable` is an interface for "a piece of code to run", with one method,
  `run()`; the tests pass lambdas such as `() -> Integer.parseInt("x")`.
  `NumberFormatException` is a subclass of `IllegalArgumentException`, so
  that one counts as `"bad argument"`.
- `public static String closeOrder()` — uses try-with-resources with two
  `AutoCloseable`s, named A and B and declared in that order, and returns the
  order they closed in, which should be `"B,A"`. Each one's `close()` can
  record its name, for example by appending it to a `StringBuilder` or a list
  that the method reads afterwards.
