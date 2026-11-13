---
title: "Paper 3: concurrency, I/O and metadata"
summary: The last three Gold domains, with the failure modes that only show up under load or at runtime.
order: 3
files: [GoldPaper3.java]
run: javac GoldPaper3.java && java GoldPaper3
hints:
  - "`parallelSum` should be correct under parallelism - an AtomicLong, or simply `values.parallelStream().mapToLong(...).sum()`, which needs no shared state at all."
  - "`wordCount` must close the stream from Files.lines, so wrap it in try-with-resources."
  - "`annotatedNames` needs the annotation retained at RUNTIME, or reflection sees nothing."
  - "`safely` catches Exception and returns the fallback - it is the pattern behind every 'do not let one task kill the pool'."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **atomic** | one indivisible step; `count++` is not |
| **shared mutable state** | data several threads change; a stream without it parallelises safely |
| **parallel stream** | a stream run on several threads |
| **shut down** | an executor must be shut down, in a `finally`, or the program never exits |
| **open file** | `Files.lines` keeps the file open until the stream is closed |
| **checked `IOException`** | handle it, declare it, or wrap it in `UncheckedIOException` |
| **retention** | annotations default to `CLASS`; reflection needs `RUNTIME` |
| **no defined order** | `getDeclaredMethods` returns methods in any order: sort them |
| **fallback** | the value returned when a task fails |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac GoldPaper3.java && java GoldPaper3` | builds and runs this paper's file |

### Java names

| Name | What it does |
|---|---|
| `values.parallelStream().mapToLong(Integer::longValue).sum()` | a parallel sum |
| `AtomicInteger`, `synchronized`, `volatile` | atomic counter; lock; visibility only |
| `try (Stream<String> lines = Files.lines(path)) { }` | reads lines and closes the file |
| `line.split("\\s+")` | the words on a line |
| `@Retention(RetentionPolicy.RUNTIME) @interface Checked {}` | an annotation reflection can see |
| `m.isAnnotationPresent(Checked.class)` | does the method carry it |
| `Callable<T>`, `task.call()` | a task that returns a value; run it |
| `e.getCause()` | the exception inside a wrapper |

### Errors

| Error | Means |
|---|---|
| `IOException`, `UncheckedIOException` | a file problem; its unchecked wrapper |
| `Exception` | caught broadly in `safely`, which returns the fallback for any failure |

---

The last paper: threads, files and reflection — the three areas where a program
compiles perfectly and then behaves differently depending on timing, the
filesystem, or what the class file kept.

## Worth re-reading

- **`count++` is not atomic.** Three operations, interleavable. `AtomicInteger`
  or `synchronized`, and `volatile` alone is not enough — it gives visibility,
  not atomicity.
- **A stream with no shared mutable state parallelises safely.** The best fix
  for a racy accumulator is usually to not have one.
- **Shut executors down**, in a `finally`. Their threads are non-daemon and a
  forgotten pool keeps the JVM alive.
- **`Files.lines` holds the file open.** Use try-with-resources, or leak a
  handle per call.
- **`IOException` is checked**; `UncheckedIOException` exists for wrapping it
  where a functional interface forbids checked exceptions.
- **Annotations default to `CLASS` retention**, which reflection cannot see.
- **`getDeclaredMethods` has no defined order.** Sort if you compare.

Two of the rules, as output. Treat it as a practice question: cover the output, write down what you expect each line to be, then compare.

```java
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.stream.LongStream;
import java.util.stream.Stream;

public class GoldConcurrency {
    public static void main(String[] args) {
        // no shared state, so parallel is safe and exact
        System.out.println(LongStream.rangeClosed(1, 1_000_000).parallel().sum());

        try {
            Stream.of("x").forEach(s -> {
                try {
                    throw new IOException("disk");
                } catch (IOException e) {
                    throw new UncheckedIOException(e);   // forEach forbids checked
                }
            });
        } catch (UncheckedIOException e) {
            System.out.println("wrapped: " + e.getCause().getMessage());
        }
    }
}
```

```output
500000500000
wrapped: disk
```

The working: the parallel stream splits the range across threads, but each
part is summed separately and the parts are combined at the end, so no two
threads ever update the same variable, and the total is exactly
`1 + 2 + ... + 1,000,000`. The lambda given to `forEach` is a `Consumer`,
whose `accept` method declares no checked exceptions, so the `IOException`
cannot escape it as itself. Wrapped in `UncheckedIOException` it can, and the
caller unwraps it with `getCause()`.

## Your turn

In `GoldPaper3.java`:

- `public static long parallelSum(List<Integer> values)` — the total, computed
  with a parallel stream and exact under load; 0 for an empty list
- `public static long wordCount(Path path)` — the number of words in the
  file, read with `Files.lines` and with the stream closed. Words are
  separated by any amount of whitespace, and blank lines contain none.
- `@interface Checked` retained at runtime, and a nested
  `public static class Sample` whose methods `alpha()` and `beta()` carry
  `@Checked` and whose method `gamma()` does not
- `public static List<String> annotatedNames(Class<?> type)` — the names of
  the type's declared methods carrying `@Checked`, sorted (for `Sample`,
  `["alpha", "beta"]`)
- `public static <T> T safely(Callable<T> task, T fallback)` — the task's
  result, or the fallback if it throws any exception, checked or unchecked
