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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **PECS** | Producer Extends, Consumer Super (Gold lesson 1) |
| **`? extends T`** | read `T`s out; you cannot add (except `null`) |
| **`? super T`** | write `T`s in; what you read is only an `Object` |
| **invariance** | `List<Integer>` is not a `List<Number>` |
| **erasure** | type arguments vanish at run time: no `new T()`, no `new T[]`, no `instanceof List<String>` |
| **equals/hashCode contract** | equal objects must have equal hash codes, or hash collections lose them |
| **immutable list** | `List.of(...)` throws on `add` |
| **generic class with two parameters** | `Pair<A, B>` |
| **frequency** | how many times each item appears |
| **intersection** | the items in both lists |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac GoldPaper1.java && java GoldPaper1` | builds and runs this paper's file |

### Java names

| Name | What it does |
|---|---|
| `static <T> void copy(List<? extends T> src, List<? super T> dst)` | PECS in one header |
| `public static class Pair<A, B>` | a nested generic class |
| `Objects.equals(a, b)` | equality that is safe when either is `null` |
| `Objects.hash(a, b)` | a hash code built from several fields |
| `map.merge(item, 1, Integer::sum)` | the counting idiom |
| `map.computeIfAbsent(k, f)` | the grouping idiom |
| `HashSet`, `LinkedHashSet` | sets: no order / first-seen order |

### Errors

| Error | Means |
|---|---|
| `UnsupportedOperationException` | changing an immutable collection |

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

Each rule, as a line of output. Treat it as a practice question: cover the output, write down what you expect each line to be, then compare.

```java
import java.util.ArrayList;
import java.util.List;

public class GoldRules {
    public static void main(String[] args) {
        List<Integer> fixed = List.of(1, 2);
        try {
            fixed.add(3);
        } catch (UnsupportedOperationException e) {
            System.out.println("List.of is immutable");
        }

        List<? extends Number> producer = new ArrayList<Integer>(List.of(1, 2));
        Number first = producer.get(0);
        producer.add(null);                     // the only thing you may add
        System.out.println(first + " " + producer.size());

        List<? super Integer> consumer = new ArrayList<Number>();
        consumer.add(5);
        Object back = consumer.get(0);          // only known to be an Object
        System.out.println(back);
    }
}
```

```output
List.of is immutable
1 3
5
```

The working: `List.of` rejected `add` at run time, although it compiled.
Through `? extends Number`, reading gives a `Number`, and the only value that
can be added is `null`, since `null` belongs to every type; the list now has
three entries. Through `? super Integer`, adding an `Integer` is fine, but
reading back only promises an `Object`, so `back` cannot be declared as an
`Integer` without a cast.

## Your turn

In `GoldPaper1.java`:

- `public static <T> void copy(List<? extends T> src, List<? super T> dst)` —
  add every element of `src`, in order, to the **end** of `dst`, keeping what
  `dst` already held; `dst` may be a wider list, such as a `List<Number>` for
  `Integer`s
- `public static class Pair<A, B>` (nested in `GoldPaper1`) with a constructor
  taking both values, `getFirst`, `getSecond`, and a correct
  `equals`/`hashCode`: pairs with equal parts are equal and share a hash
  code, a pair never equals something that is not a pair, and two equal pairs
  added to a `HashSet` count once. `Objects.equals(a, b)` compares two values
  safely even when one is `null`, and `Objects.hash(a, b)` combines hash codes.
- `public static <T> Map<T, Integer> frequency(List<T> items)` — how many
  times each item occurs; an empty map for an empty list
- `public static <T> List<T> intersection(List<T> a, List<T> b)` — the items
  of `a` that also appear in `b`, each once, in the order they first appear
  in `a`: `{1, 2, 3}` and `{3, 2, 9}` give `[2, 3]`
