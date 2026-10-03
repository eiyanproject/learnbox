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

Two threads incrementing the same `int` lose updates. Not sometimes in theory —
reliably, at scale.

```java
count++;     // read, add, write: three steps, and another thread can interleave
```

`++` is not atomic. Two threads can both read 5, both compute 6, and both write
6. One increment vanished.

## Making it safe

Three tools, in increasing order of preference:

```java
synchronized (lock) { count++; }          // a mutex you manage
AtomicInteger count = new AtomicInteger(); count.incrementAndGet();
LongAdder adder;                          // better under heavy contention
```

`synchronized` guarantees mutual exclusion **and** visibility — changes made
inside are visible to the next thread that enters. `volatile` gives visibility
only, not atomicity, so a `volatile int` counter is still wrong.

The atomic classes use a compare-and-set loop in hardware: no lock, no blocking,
and correct.

## Executors, not raw threads

```java
ExecutorService pool = Executors.newFixedThreadPool(4);
try {
    List<Future<Integer>> results = pool.invokeAll(tasks);
} finally {
    pool.shutdown();
}
```

`new Thread(...).start()` gives you no pooling, no queueing, no result and no
way to wait. An `ExecutorService` gives all four, and `Callable<T>` returns a
value where `Runnable` cannot.

**Always shut it down.** A pool's threads are non-daemon by default, so a
program that forgets never exits. `shutdown()` finishes queued work;
`shutdownNow()` attempts to interrupt.

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
remembering.

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

## Your turn

In `Concurrent.java`:

- `public static int racyCount(int threads, int perThread)` — deliberately
  unsynchronised
- `public static int safeCount(int threads, int perThread)` — always correct
- `public static List<Integer> runAll(List<Callable<Integer>> tasks)` — run on
  an executor, return the results in order, shut the pool down
- `public static Map<String, Integer> concurrentTally(List<String> words)` —
  count using a `ConcurrentHashMap`
