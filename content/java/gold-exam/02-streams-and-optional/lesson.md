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

## Your turn

In `GoldPaper2.java`:

- `public static double averageLength(List<String> items)` — 0 for an empty
  list
- `public static Map<Character, List<String>> namesByInitial(List<String> items)`
- `public static long countLongerThan(List<String> items, int n)`
- `public static String summarise(List<String> items)` — `"first..last (n)"`,
  or `"none"` when empty
- `public static List<String> topN(List<String> items, int n)` — longest first,
  ties alphabetical
