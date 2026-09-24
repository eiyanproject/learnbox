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

## Your turn

In `GoldPaper3.java`:

- `public static long parallelSum(List<Integer> values)` — correct under
  parallelism
- `public static long wordCount(Path path)` — words in a file, stream closed
- `@interface Checked` retained at runtime, and a `Sample` class using it
- `public static List<String> annotatedNames(Class<?> type)` — sorted
- `public static <T> T safely(Callable<T> task, T fallback)` — the fallback on
  any exception
