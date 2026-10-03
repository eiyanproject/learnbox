---
title: Streams
summary: A pipeline of source, intermediate operations and one terminal operation - and why nothing happens until the last one.
order: 4
files: [Pipe.java]
run: javac Pipe.java && java Pipe
hints:
  - "`longNames` is filter then map then collect: `items.stream().filter(s -> s.length() > n).map(String::toUpperCase).collect(Collectors.toList())`."
  - "`total` uses mapToInt(String::length).sum() - mapToInt gives an IntStream, which has sum() where a Stream<Integer> does not."
  - "`groupByLength` is `Collectors.groupingBy(String::length)`, which returns a Map<Integer, List<String>>."
  - "`firstMatching` returns an Optional: `stream().filter(test).findFirst()`. Do not call .get() on it - return the Optional itself."
---

A stream is a pipeline, not a collection. It holds no data; it describes work
to do on a source.

```java
List<String> result = items.stream()      // source
    .filter(s -> s.length() > 3)          // intermediate - lazy
    .map(String::toUpperCase)             // intermediate - lazy
    .collect(Collectors.toList());        // terminal - runs everything
```

## Lazy until the terminal operation

Intermediate operations return a new stream and do nothing else. Until a
terminal operation runs, no element has been touched. This is why:

```java
items.stream().map(String::toUpperCase);    // does absolutely nothing
```

and why a pipeline can short-circuit — `findFirst` after a `filter` stops at
the first match rather than filtering the whole list.

A stream can be consumed **once**. Reusing one throws
`IllegalStateException`.

## The operations worth knowing

| Intermediate | |
|---|---|
| `filter(Predicate)` | keep matches |
| `map(Function)` | transform |
| `flatMap(Function)` | flatten nested streams |
| `distinct()`, `sorted()`, `limit(n)`, `skip(n)` | |
| `peek(Consumer)` | look without consuming — for debugging |

| Terminal | |
|---|---|
| `collect(Collectors...)` | into a collection or map |
| `forEach(Consumer)` | side effects |
| `reduce(identity, op)` | fold to one value |
| `count()`, `anyMatch`, `allMatch`, `noneMatch` | |
| `findFirst()`, `findAny()` | an `Optional` |
| `min`, `max` | an `Optional` |

## Primitive streams

`mapToInt`, `mapToLong`, `mapToDouble` give you `IntStream` and friends, which
add `sum()`, `average()` and `summaryStatistics()` and avoid boxing. A plain
`Stream<Integer>` has no `sum()` — a question the exam asks in exactly that
form.

## Collectors

```java
Collectors.toList()
Collectors.toSet()
Collectors.joining(", ")
Collectors.groupingBy(String::length)          // Map<Integer, List<String>>
Collectors.partitioningBy(s -> s.isEmpty())    // Map<Boolean, List<String>>
Collectors.counting()
```

`groupingBy` takes a downstream collector too:
`groupingBy(String::length, Collectors.counting())`.

## Run

```java
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Streams {
    public static void main(String[] args) {
        List<String> items = List.of("ab", "abcd", "xyz", "hello");

        Stream<String> lazy = items.stream().peek(s -> System.out.println("saw " + s));
        System.out.println("nothing yet");
        System.out.println(lazy.filter(s -> s.length() > 3).findFirst().orElse("none"));

        Stream<String> once = items.stream();
        once.count();
        try {
            once.count();
        } catch (IllegalStateException e) {
            System.out.println("reused: IllegalStateException");
        }

        Map<Integer, Long> byLength = items.stream()
            .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting()));
        System.out.println(byLength);
        System.out.println(items.stream().mapToInt(String::length).sum());
        System.out.println(items.stream().collect(Collectors.joining(", ")));
    }
}
```

```output
nothing yet
saw ab
saw abcd
abcd
reused: IllegalStateException
{2=1, 3=1, 4=1, 5=1}
14
ab, abcd, xyz, hello
```

`xyz` and `hello` were never seen: `findFirst` stopped the pipeline.

## Your turn

In `Pipe.java`:

- `public static List<String> longNames(List<String> items, int n)` — longer
  than `n`, uppercased
- `public static int total(List<String> items)` — the sum of their lengths
- `public static Map<Integer, List<String>> groupByLength(List<String> items)`
- `public static Optional<String> firstMatching(List<String> items, Predicate<String> test)`
- `public static String joined(List<String> items)` — comma-separated
