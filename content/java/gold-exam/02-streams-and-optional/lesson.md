---
title: "Paper 2: streams, lambdas and Optional"
summary: Laziness, the terminal operation that actually runs it, and the Optional habits that give back the safety.
order: 2
files: [GoldPaper2.java]
run: javac GoldPaper2.java && java GoldPaper2
hints:
  - "`averageLength` returns an OptionalDouble from `mapToInt(String::length).average()` - convert to a double with orElse(0) rather than get()."
  - "`namesByInitial` is `groupingBy(s -> s.charAt(0))`, which gives Map<Character, List<String>>."
  - "`countLongerThan` can use `filter(...).count()`, which returns a long."
  - "`summarise` should return \"none\" for an empty list - reduce with an identity, or findFirst and map, but do not call get() on an empty Optional."
---

The second Gold paper: pipelines and absence.

## Worth re-reading

- **Nothing runs until the terminal operation.** A pipeline with no terminal
  operation does no work at all, and one with a terminal operation may not
  touch every element — `findFirst` after a `filter` stops early.
- **A stream is consumed once.** Reusing it throws `IllegalStateException`.
- **`Stream<Integer>` has no `sum()`.** `mapToInt` gives an `IntStream`, which
  has `sum`, `average` and `summaryStatistics`.
- **`average()` returns an `OptionalDouble`**, because the average of nothing
  is not zero — it does not exist.
- **`orElse` always evaluates its argument; `orElseGet` does not.** With a
  costly default, that is a bug and not a preference.
- **`Collectors.toList()` makes no promise about mutability**;
  `Stream.toList()` (Java 16+) is explicitly unmodifiable.
- **`peek` is for debugging.** Using it for side effects on a pipeline that may
  short-circuit gives results that depend on the terminal operation.

Each rule, as a line of output. Treat it as a practice question: cover the output, write down what you expect each line to be, then compare.

```java
import java.util.ArrayList;
import java.util.List;
import java.util.OptionalDouble;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class GoldStreams {
    public static void main(String[] args) {
        OptionalDouble none = IntStream.empty().average();
        System.out.println(none.isPresent());
        System.out.println(IntStream.of(2, 4).average().getAsDouble());

        List<Integer> fixed = Stream.of(3, 1).toList();
        try {
            fixed.add(2);
        } catch (UnsupportedOperationException e) {
            System.out.println("toList() is unmodifiable");
        }

        List<String> seen = new ArrayList<>();
        Stream.of("a", "b", "c").peek(seen::add).anyMatch(s -> s.equals("b"));
        System.out.println(seen);               // "c" was never reached
    }
}
```

```output
false
3.0
toList() is unmodifiable
[a, b]
```

The working: the average of an empty stream is an empty `OptionalDouble`,
not 0. The average of 2 and 4 is present, and `getAsDouble()` takes it out
(safe here only because the stream was not empty). `Stream.toList()` refused
`add`. And `anyMatch` stopped as soon as `"b"` matched, so `peek` never saw
`"c"`: a `peek` that collected every element "for later" would have
silently missed one.

## Your turn

In `GoldPaper2.java`:

- `public static double averageLength(List<String> items)` — the average
  length of the strings (`"ada"` and `"grace"` give 4.0); 0 for an empty list,
  without throwing
- `public static Map<Character, List<String>> namesByInitial(List<String> items)`
  — the items grouped by first character, each group in original order; an
  empty map for an empty list
- `public static long countLongerThan(List<String> items, int n)` — how many
  items are strictly longer than `n` (a string of exactly `n` does not count)
- `public static String summarise(List<String> items)` — the first item, two
  dots, the last item, and the count in brackets: `{"a", "b", "c"}` gives
  `"a..c (3)"` and `{"a"}` gives `"a..a (1)"`; `"none"` when empty
- `public static List<String> topN(List<String> items, int n)` — the `n`
  longest items, longest first, ties in alphabetical order; if `n` is larger
  than the list, all of them (`limit(n)` handles that)
