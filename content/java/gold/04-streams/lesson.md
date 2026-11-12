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

Most loops over a collection do one of a few things: keep some elements,
transform each one, and gather the results, or add them up. Written as a loop,
the *how* (an empty list, a counter, an `if`, an `add`) hides the *what*:

```java
List<String> result = new ArrayList<>();
for (String s : items) {
    if (s.length() > 3) {
        result.add(s.toUpperCase());
    }
}
```

A **stream** says only the what, as a chain of named steps:

```java
List<String> result = items.stream()      // source
    .filter(s -> s.length() > 3)          // intermediate - lazy
    .map(String::toUpperCase)             // intermediate - lazy
    .collect(Collectors.toList());        // terminal - runs everything
```

(Fragments: `items` is a `List<String>`.) Both produce the same list. Each
loop line has a stream counterpart: the `if` is `filter`, the
`s.toUpperCase()` is `map`, and the empty list plus `add` is `collect`. Read
the stream from top to bottom as a sentence: take the items, keep those
longer than 3, upper-case them, and collect them into a list.

Why bother, when the loop works? Because the stream version:

1. **states the intent**: "filter, map, collect" are named steps, where the
   loop makes you work out from its `if` and `add` what it is for;
2. **leaves no scaffolding to get wrong**: no empty list to remember, no
   counter, no mutable state shared across rounds;
3. **does not change the source**: `items` is untouched;
4. **gives a shared vocabulary**: two people saying "filter" mean the same
   operation.

The loop is called **external iteration**: your code drives the loop and
pulls each element out itself. The stream is **internal iteration**: you hand
the library the operations, and it does the looping, which is also what
lets it run them lazily, or in parallel.

A stream is a pipeline, not a collection. It holds no data; it describes work
to do on a **source**, here the list. Each step takes a function (a lambda or
a method reference, from the previous lesson) that says what to do with each
element.

## Lazy until the terminal operation

Operations come in two kinds. **Intermediate** operations, such as `filter`
and `map`, return a new stream. **Terminal** operations, such as `collect`,
`count` or `forEach`, produce a result (or a side effect) and end the stream.
A pipeline is a source, any number of intermediate operations, and exactly
one terminal operation.

Intermediate operations return a new stream and do nothing else. Until a
terminal operation runs, no element has been touched. This is called being
**lazy**. This is why:

```java
items.stream().map(String::toUpperCase);    // does absolutely nothing
```

and why a pipeline can **short-circuit** — `findFirst` after a `filter` stops
at the first match rather than filtering the whole list. Elements also travel
through the pipeline one at a time: the first element goes through `filter`
and `map` before the second is even looked at, rather than the whole list
being filtered first and then mapped.

A stream can be consumed **once**. Reusing one throws
`IllegalStateException` ("stream has already been operated upon or closed").
Call `items.stream()` again for a second pipeline.

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
form. The reason is that `Stream<T>` works for any `T`, and "sum" means
nothing for a stream of, say, `File`s; only a stream that is known to hold
numbers can offer it. `average()` returns an `OptionalDouble`, since an empty
stream has no average.

`Optional<T>`, which `findFirst`, `min` and `max` return, is a box that holds
either one value or nothing. It stands for "there may be no answer", in place
of returning `null`; the next lesson covers it in full. `orElse("none")`, in
the program below, takes the value out, or uses `"none"` if there is none.

## Collectors

```java
Collectors.toList()
Collectors.toSet()
Collectors.joining(", ")
Collectors.groupingBy(String::length)          // Map<Integer, List<String>>
Collectors.partitioningBy(s -> s.isEmpty())    // Map<Boolean, List<String>>
Collectors.counting()
```

A **collector** says how to gather a stream's elements into a final result.
`groupingBy(f)` puts each element in a list under the key `f` gives for it;
`partitioningBy(p)` is the same with only two keys, `true` and `false`.
`joining(", ")` joins strings with that separator between them (and nothing
before the first or after the last).

`groupingBy` takes a downstream collector too:
`groupingBy(String::length, Collectors.counting())`. The **downstream
collector** says what to do with each group instead of making a list of it:
here, count it, giving a `Map<Integer, Long>` of length to how many words had
that length.

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

Following it through. Creating `lazy` with a `peek` printed nothing:
"nothing yet" came first. Only the terminal `findFirst` started the work, and
the elements went through one at a time: `ab` was seen and failed the filter,
`abcd` was seen and passed, and `findFirst` had its answer. Calling `count()`
twice on `once` threw on the second call. `groupingBy` with a `TreeMap::new`
argument collected into a `TreeMap`, so the lengths print sorted, and
`counting()` counted each group. `mapToInt` turned the strings into their
lengths, `2 + 4 + 3 + 5`, which `sum()` added to 14.

## Your turn

In `Pipe.java`:

Write each one as a single stream pipeline:

- `public static List<String> longNames(List<String> items, int n)` — the
  items strictly longer than `n` (exactly `n` characters does not count),
  uppercased, in order: `{"ada", "grace", "alan"}` with 3 gives
  `["GRACE", "ALAN"]`
- `public static int total(List<String> items)` — the sum of their lengths,
  `0` for an empty list
- `public static Map<Integer, List<String>> groupByLength(List<String> items)`
  — a map from each length to the items of that length, in their original
  order; only lengths that actually occur appear as keys
- `public static Optional<String> firstMatching(List<String> items, Predicate<String> test)`
  — the first item that passes `test`, as an `Optional`; when nothing matches,
  an empty `Optional`, never `null`
- `public static String joined(List<String> items)` — the items separated by
  a single comma with **no space**: `"a,b,c"`; one item gives `"a"`, and none
  gives `""`
