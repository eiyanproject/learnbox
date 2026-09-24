---
title: "Paper 1: generics and collections"
summary: Wildcards, erasure and the equals/hashCode contract, mixed and unlabelled.
order: 1
files: [GoldPaper1.java]
run: javac GoldPaper1.java && java GoldPaper1
hints:
  - "`copy(List<? extends T> src, List<? super T> dst)` is PECS in one signature: read from the producer, write to the consumer."
  - "`Pair<A, B>` needs equals and hashCode that agree - `Objects.equals` and `Objects.hash` do both correctly in one line each."
  - "`frequency` counts occurrences into a Map; `merge(item, 1, Integer::sum)` is the idiom."
  - "`intersection` keeps items present in both lists, without duplicates, in first-seen order - a LinkedHashSet plus a contains check."
---

The first Gold paper: type parameters, wildcards, and the collection contracts.

## Worth re-reading

- **PECS.** `? extends` produces values you read; `? super` consumes values you
  write. You cannot add to a `List<? extends T>` (except `null`), and anything
  read from a `List<? super T>` is only an `Object`.
- **`List<Integer>` is not a `List<Number>`.** Generics are invariant, which is
  the reason wildcards exist at all.
- **Erasure** means no `new T()`, no `new T[]`, and no
  `instanceof List<String>`.
- **equals and hashCode must agree.** Equal objects must have equal hashes, or
  hash-based collections lose them. A `record` generates both.
- **`Map.merge` and `computeIfAbsent`** replace the check-then-put dance, and
  are atomic on a `ConcurrentHashMap` where the manual version is not.
- **`List.of(...)` is immutable.** Adding to it throws
  `UnsupportedOperationException` — a favourite question, because the code
  compiles perfectly.

## Your turn

In `GoldPaper1.java`:

- `public static <T> void copy(List<? extends T> src, List<? super T> dst)`
- `public static class Pair<A, B>` with `getFirst`, `getSecond`, and a correct
  `equals`/`hashCode`
- `public static <T> Map<T, Integer> frequency(List<T> items)`
- `public static <T> List<T> intersection(List<T> a, List<T> b)` — no
  duplicates, first-seen order
