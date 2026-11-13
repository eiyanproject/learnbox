---
title: Threads, executors and safe sharing
summary: Why two threads incrementing a counter lose updates, what an ExecutorService gives you over raw threads, and the collections that are safe to share.
order: 6
files: [Concurrent.java]
run: javac Concurrent.java && java Concurrent
hints:
  - "`racyCount` is meant to be wrong sometimes: a plain int++ from several threads loses updates. Use a plain field and no synchronisation."
  - "`safeCount` should use AtomicInteger's incrementAndGet, or a synchronized block - either fixes it."
  - "`runAll` submits each task to an ExecutorService, waits for all of them, and shuts it down. `invokeAll` does the waiting for you."
  - "Always shut an executor down in a finally block, or the JVM keeps its non-daemon threads alive and the program never exits."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **thread** | a separate line of execution inside one program; threads share memory |
| **concurrency** | several things in progress at once |
| **core** | one processing unit of the CPU; each runs one thing at a time |
| **atomic** | one indivisible step that no other thread can interrupt; `count++` is not |
| **interleave** | two threads' steps mixing in time |
| **lost update** | two threads read the same value and one write overwrites the other |
| **race condition** | a result that depends on the exact timing of threads |
| **mutual exclusion** | only one thread at a time may run a piece of code |
| **lock** / **mutex** | the object that enforces mutual exclusion |
| **visibility** | whether one thread's write is seen by another; `synchronized` guarantees it |
| **stale value** | an old copy a thread keeps using instead of the latest write |
| **`volatile`** | gives visibility only, not atomicity |
| **compare-and-set** | "set to 6 only if it is still 5", retried; how atomic classes work without locks |
| **contention** | many threads competing for the same thing |
| **executor** | runs tasks for you, on a pool of threads |
| **thread pool** | a fixed set of reusable threads; extra tasks queue |
| **task** | a unit of work: a `Runnable` (no result) or a `Callable` (returns one) |
| **`Future`** | a handle to a result that may not exist yet |
| **daemon thread** | one the JVM does not wait for; pool threads are not daemons, so pools must be shut down |
| **platform thread** | an ordinary thread supplied by the operating system; costly |
| **virtual thread** | a cheap thread managed by the JVM (Java 21); good for tasks that mostly wait |
| **block** (a thread) | wait for the network, a file or `sleep` |
| **thread safe** | correct when used by several threads at once |
| **check-then-act** | two calls that must happen together; another thread can act in between |
| **parallel stream** | a stream whose work is split across threads automatically |
| **join** | wait for a thread to finish |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Concurrent.java && java Concurrent` | builds and runs this lesson's file |

### Java classes and methods

| Name | What it does |
|---|---|
| `synchronized (lock) { count++; }` | one thread at a time in the block |
| `synchronized` method | locks on the object itself |
| `AtomicInteger`, `incrementAndGet()`, `get()` | a thread-safe counter; add one and return it; read it |
| `LongAdder` | a counter that is faster under heavy contention |
| `new Thread(runnable).start()`, `thread.join()` | start a raw thread; wait for it |
| `Executors.newFixedThreadPool(4)` | a pool of four threads |
| `pool.submit(task)`, `pool.invokeAll(tasks)` | run one task; run all and wait, results in task order |
| `future.get()` | waits for and returns the result |
| `pool.shutdown()`, `shutdownNow()` | finish queued work and stop; try to interrupt running tasks |
| `Executors.newVirtualThreadPerTaskExecutor()` | a new virtual thread for each task |
| `Thread.sleep(1000)` | pauses the thread for one second |
| `ConcurrentHashMap` | a thread-safe map; `merge` and `compute` are atomic |
| `CopyOnWriteArrayList` | a thread-safe list for many reads and rare writes |
| `Collections.synchronizedList(...)` | wraps a list in one coarse lock |
| `words.parallelStream()` | a stream processed on several threads |
| `int id = t;` | a fresh effectively-final copy for a lambda to capture |
| `throws Exception` | lets `main` pass checked exceptions on |

### Errors

| Error | Means |
|---|---|
| `InterruptedException` | a waiting thread was interrupted; checked |
| `ExecutionException` | thrown by `future.get()`, wrapping what the task threw |
| `ConcurrentModificationException` | a collection was changed while being iterated |
| *(no error at all)* | a race condition: wrong totals that differ from run to run |

---

A **thread** is a separate line of execution inside one program. Several
threads let a program do several things at once, such as serving many users
or using every core of the processor, and they all share the program's
memory. That sharing is what makes threads both useful and dangerous, as the
simplest example shows: two threads incrementing the same `int` lose updates.
Not sometimes in theory — reliably, at scale.

```java
count++;     // read, add, write: three steps, and another thread can interleave
```

`++` is not **atomic**: it is not one indivisible step. Two threads can both
read 5, both compute 6, and both write 6. One increment vanished:

```text
thread A: reads 5
thread B: reads 5
thread A: writes 6
thread B: writes 6      two increments, but count only went up by one
```

This is a **race condition**: the result depends on the exact timing of the
threads, so the same code gives different answers on different runs, and
usually works in small tests.

## Making it safe

Three tools, in increasing order of preference:

```java
synchronized (lock) { count++; }          // a mutex you manage
AtomicInteger count = new AtomicInteger(); count.incrementAndGet();
LongAdder adder;                          // better under heavy contention
```

(Three alternatives, one per line.)

`synchronized (lock) { ... }` lets only one thread at a time run the block for
a given `lock` object; any other thread that arrives waits until the first one
leaves. That is **mutual exclusion**, and a lock used this way is a **mutex**.
A method can be declared `synchronized` too, which locks on the object itself.

`synchronized` guarantees mutual exclusion **and** visibility — changes made
inside are visible to the next thread that enters. Visibility is the less
obvious half: without it, a thread may keep working with a stale copy of a
value cached by its own processor core, and never see another thread's
write. `volatile` on a field gives visibility only, not atomicity, so a
`volatile int` counter is still wrong: every thread sees the latest value, but
two of them can still read the same one before either writes.

The atomic classes in `java.util.concurrent.atomic` use a compare-and-set loop
in hardware: "set it to 6, but only if it is still 5", retried if another
thread got there first. No lock, no blocking, and correct.
`incrementAndGet()` adds one and returns the new value. `LongAdder` spreads
the count over several cells that are added up on reading, which is faster
when very many threads update at once.

## Executors, not raw threads

```java
ExecutorService pool = Executors.newFixedThreadPool(4);
try {
    List<Future<Integer>> results = pool.invokeAll(tasks);
} finally {
    pool.shutdown();
}
```

(A fragment: `tasks` is a `List<Callable<Integer>>`.) An **executor** runs
tasks for you on a **thread pool**, a fixed set of threads that are reused
from task to task. `newFixedThreadPool(4)` makes one with four threads; give
it a hundred tasks and it runs four at a time, queueing the rest.

`new Thread(...).start()` gives you no pooling, no queueing, no result and no
way to wait. An `ExecutorService` gives all four, and `Callable<T>` returns a
value where `Runnable` cannot. Starting a thread is expensive, so reusing a
few pays off quickly.

Submitting a task returns a `Future<T>`: a handle to a result that may not
exist yet. `future.get()` waits until the task has finished and returns its
result, or throws an `ExecutionException` wrapping whatever the task threw.
`invokeAll(tasks)` submits every task and waits for all of them, returning
their futures in the same order as the tasks.

**Always shut it down.** A pool's threads are non-daemon by default, so a
program that forgets never exits. (A **daemon** thread is one the JVM does not
wait for; the JVM exits only when every non-daemon thread has finished, and a
pool's idle threads never finish by themselves.) `shutdown()` finishes queued
work and then stops the threads; `shutdownNow()` attempts to interrupt the
running ones. The `try` / `finally` above makes sure the pool is shut down
even if something throws.

## Virtual threads (Java 21)

Each ordinary Java thread runs on a **platform thread** supplied by the
operating system, and those are expensive: a few megabytes of memory each,
and real work to start. A server that gives every request its own thread
runs out of threads long before it runs out of processor. That is why pools
exist, but a pool of 200 threads can only *wait* on 200 network calls at
once.

Java 21 made **virtual threads** a standard feature. They are threads managed
by the JVM rather than the operating system, so cheap that you can have a
million. Many of them share a few platform threads: whenever a virtual
thread blocks, waiting on the network, a file or `sleep`, the JVM parks it
and runs another on the same platform thread. Blocking, the thing that made
threads expensive, becomes cheap.

```java
try (ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 10_000; i++) {
        pool.submit(() -> {
            Thread.sleep(1000);        // stands in for waiting on the network
            return null;
        });
    }
}                                       // close() waits for every task
```

(A fragment from a `main` that declares `throws Exception`.) This starts a
new virtual thread for each of 10,000 tasks, each of which waits one second.
Run it, and the whole thing finishes in about one second: all 10,000 waits
overlap. A fixed pool of four platform threads would take about 2,500
seconds. (Since Java 19 an `ExecutorService` is `AutoCloseable`, so
try-with-resources shuts it down and waits for its tasks, which replaces the
`finally` with `shutdown()`.)

Virtual threads help when there are many tasks that mostly **wait**. They do
nothing for tasks that mostly **compute**: a CPU core can only do one thing
at a time, however many threads you give it. For computation, a pool sized to
the number of cores, or a parallel stream, is still the tool. Everything else
in this lesson, races, atomics, locks and concurrent collections, applies to
virtual threads exactly as to platform threads.

## Sharing collections

`ArrayList` and `HashMap` are not thread safe; concurrent modification can
corrupt them outright, not merely give stale reads. The safe choices:

| | |
|---|---|
| `ConcurrentHashMap` | a properly concurrent map |
| `CopyOnWriteArrayList` | many readers, rare writes |
| `Collections.synchronizedList(...)` | a coarse lock around everything |

`Collections.synchronizedMap` still needs external synchronisation for
check-then-act sequences; `ConcurrentHashMap` has `putIfAbsent`, `merge` and
`compute` which are atomic on their own. That is the difference worth
remembering. A **check-then-act** sequence is two calls that must happen
together: "if the key is missing, put it". With a synchronized map, each call
is safe on its own, but another thread can act between the check and the
put. `merge(w, 1, Integer::sum)` on a `ConcurrentHashMap` does the whole
read-add-write as one atomic step.

`parallelStream()` is a stream whose work is split across several threads
automatically. It is an easy way to create exactly this kind of concurrent
access, which is why this lesson's tally exercise uses one.

## Run

Four threads, ten thousand increments each, and nothing lost:

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class Counting {
    public static void main(String[] args) throws Exception {
        AtomicInteger count = new AtomicInteger();
        ExecutorService pool = Executors.newFixedThreadPool(4);
        try {
            List<Callable<Integer>> tasks = new ArrayList<>();
            for (int t = 0; t < 4; t++) {
                int id = t;
                tasks.add(() -> {
                    for (int i = 0; i < 10_000; i++) count.incrementAndGet();
                    return id;
                });
            }
            int ids = 0;
            for (Future<Integer> f : pool.invokeAll(tasks)) ids += f.get();
            System.out.println(count.get() + " increments, ids summed to " + ids);
        } finally {
            pool.shutdown();
        }

        ConcurrentHashMap<String, Integer> words = new ConcurrentHashMap<>();
        for (String w : "a b a".split(" ")) words.merge(w, 1, Integer::sum);
        System.out.println(words.get("a"));
    }
}
```

```output
40000 increments, ids summed to 6
2
```

With a plain `int` and `count++` the total comes out below 40000, by a
different amount each run - which is why it cannot be shown as a fixed output.

Two details in the program. `int id = t;` copies the loop variable into a
fresh variable each round, because a lambda may only capture an effectively
final local, and `t` changes. And `main` declares `throws Exception`, because
`invokeAll` and `get` throw checked exceptions (`InterruptedException`,
`ExecutionException`) that this small example does not handle.

## Your turn

In `Concurrent.java`:

- `public static int racyCount(int threads, int perThread)` — start
  `threads` threads that each add one to a shared plain `int` field
  `perThread` times, wait for them all (`thread.join()`), and return the
  total. Deliberately unsynchronised: the tests only check that the result is
  never more than `threads * perThread`, and is exact with one thread.
- `public static int safeCount(int threads, int perThread)` — the same, but
  always exactly `threads * perThread` (0 when there is no work)
- `public static List<Integer> runAll(List<Callable<Integer>> tasks)` — run
  every task on an executor, return their results in the same order as the
  tasks, and shut the pool down (in a `finally`). An empty list of tasks
  gives an empty list.
- `public static Map<String, Integer> concurrentTally(List<String> words)` —
  how many times each word appears, counted into a `ConcurrentHashMap` from a
  `parallelStream()` with `merge`. A test feeds it 20,000 words and expects
  every one counted.
