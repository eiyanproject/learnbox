---
title: The collections framework
summary: List, Set, Map and Deque, which implementation to reach for, and the equals and hashCode contract that makes them work.
order: 2
files: [Store.java]
run: javac Store.java && java Store
hints:
  - "`countWords` lowercases, splits on whitespace, and counts with `map.merge(word, 1, Integer::sum)` - the cleanest form of the count idiom."
  - "`firstUnique` needs insertion order preserved, so count with a LinkedHashMap and then find the first entry with a count of 1."
  - "`sortedByValue` returns a List<Map.Entry<String,Integer>> sorted by value descending, then key ascending - a Comparator with thenComparing."
  - "`dedupe` keeps first-seen order: a LinkedHashSet does it in one line."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **collections framework** | the interfaces and classes in `java.util` for groups of objects |
| **interface** vs **implementation** | what a collection can do (`List`) vs how it does it (`ArrayList`) |
| **`List`** | ordered, duplicates allowed, reached by index |
| **`Set`** | no duplicates; asks "is it in?" |
| **`Map`** | key to value; looks up by key; not a `Collection` |
| **`Queue`** | first in, first out |
| **`Deque`** ("deck") | add and remove at both ends; also works as a stack |
| **stack** | last in, first out |
| **view** | a collection backed by a map: `keySet()`, `values()`, `entrySet()` |
| **entry** | one key-value pair, a `Map.Entry` |
| **immutable collection** | made by `List.of` and friends; adding throws |
| **Big-O** | how cost grows with size `n`: O(1) constant, O(log n) very slow growth, O(n) in proportion |
| **cache locality** | elements side by side in memory, which processors read fast; why `ArrayList` usually wins |
| **hash** | the number `hashCode()` turns an object into |
| **bucket** | the slot a hash leads to inside a `HashSet` or `HashMap` |
| **equals/hashCode contract** | equal objects must have equal hash codes |
| **collision** | unequal objects with the same hash; allowed and handled |
| **mutable key** | a key that can change after insertion; it gets lost, so use immutable keys |
| **insertion order** | the order items were first added; kept by `LinkedHash...` |
| **sorted order** | kept by `Tree...`, which needs `Comparable` elements or a `Comparator` |
| **`Comparator`** | an object that says how to order two values |
| **method reference** | `Integer::sum`: a method passed as a function (Gold lesson 3) |
| **idiom** | the usual way to write something, such as counting with `merge` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Store.java && java Store` | builds and runs this lesson's file |

### Java classes and methods

| Name | What it does |
|---|---|
| `ArrayList`, `LinkedList`, `ArrayDeque` | lists and deques |
| `HashSet`, `LinkedHashSet`, `TreeSet` | sets: no order / insertion order / sorted |
| `HashMap`, `LinkedHashMap`, `TreeMap` | maps: no order / insertion order / sorted keys |
| `Stack` | the old, legacy stack class; use `ArrayDeque` |
| `List.of(...)`, `Set.of(...)`, `Map.of(...)` | small immutable collections |
| `map.getOrDefault(k, 0)` | the value, or 0 if there is none |
| `map.putIfAbsent(k, v)` | stores `v` only if `k` has no value |
| `map.computeIfAbsent(k, key -> new ArrayList<>())` | the value, creating and storing one first if absent |
| `map.merge(k, 1, Integer::sum)` | the counting idiom: 1 if new, otherwise old + 1 |
| `entry.getKey()`, `entry.getValue()` | the two halves of an entry |
| `Map.Entry.comparingByValue()`, `comparingByKey()` | ready-made comparators for entries |
| `.reversed()`, `.thenComparing(...)` | reverse a comparator; break ties with another |
| `set.contains(x)` | `true` if `x` is in the set |
| `text.split("\\s+")` | words separated by any run of whitespace |
| `record GoodKey(String id) {}` | a key with correct `equals` and `hashCode` for free |

### Errors

| Error | Means |
|---|---|
| `UnsupportedOperationException` | tried to change an immutable collection such as `List.of(...)` |
| *(no error at all)* | `equals` without `hashCode`: the set says an object is missing when it is there |

---

Arrays have a fixed length and almost no methods. Real programs need
collections that grow, that refuse duplicates, that look things up by key,
or that keep themselves sorted. The **collections framework** in `java.util`
provides all of these, as a small set of interfaces (what a collection can
do) and several classes implementing each one (how it does it, with
different speed trade-offs). You program against the interface, `List`, and
choose the class, `ArrayList`, in one place, so it can be changed later.

Three interfaces cover nearly everything:

| | Holds | |
|---|---|---|
| `List` | ordered, duplicates allowed | index access |
| `Set` | no duplicates | membership |
| `Map` | key to value | lookup by key |

`Queue` and `Deque` add ends-based access: a **queue** hands items out in the
order they arrived (first in, first out), and a **deque** ("deck",
double-ended queue) allows adding and removing at both ends, which also makes
it a **stack** (last in, first out). `Collection` is the parent of the first
two; `Map` is deliberately **not** a `Collection`, because it holds pairs
rather than single elements. It offers views that are: `keySet()`,
`values()` and `entrySet()`, the last a set of `Map.Entry` objects, each with
`getKey()` and `getValue()`.

`List.of(...)`, `Set.of(...)` and `Map.of(...)` (Java 9) create small
**immutable** collections in one call. Trying to add to one throws
`UnsupportedOperationException`, a run-time error; copy it into an
`ArrayList` or `HashMap` first if you need to change it.

## Choosing an implementation

| Need | Use | Why |
|---|---|---|
| a general list | `ArrayList` | O(1) index, cheap iteration |
| lots of insertion at the ends | `LinkedList` / `ArrayDeque` | no shifting |
| a plain set | `HashSet` | O(1), no order |
| insertion order kept | `LinkedHashSet` / `LinkedHashMap` | predictable output |
| sorted order | `TreeSet` / `TreeMap` | O(log n), needs ordering |
| a stack or queue | `ArrayDeque` | faster than `Stack`, which is legacy |

The O(...) column is the Big-O notation for how the cost grows with the
number of elements `n`: O(1) stays the same however big the collection gets,
O(log n) grows very slowly, and O(n) grows in proportion to it. A `HashSet`
finds an element in roughly the same time whether it holds ten or ten
million.

`ArrayList` beats `LinkedList` in almost every real case, including removal,
because **cache locality** outweighs the pointer arithmetic: an `ArrayList`'s
elements sit side by side in memory, which processors read very quickly,
while a `LinkedList`'s nodes are scattered, and following each pointer is
slow. `LinkedList` is on the exam far more than it should be in your code.

A `TreeSet` or `TreeMap` keeps its elements sorted, which needs a way to
order them: either the elements implement `Comparable`, or you pass a
`Comparator` to the constructor.

## equals and hashCode

A `HashSet` or `HashMap` is fast because it does not compare a new element
with every element already stored. It calls `hashCode()`, which turns the
object into a number, and uses that number to go straight to one small
**bucket**, then calls `equals` only on the few objects in that bucket. That
works only if equal objects always produce the same number, and so lead to
the same bucket. So:

> If `a.equals(b)`, then `a.hashCode() == b.hashCode()`.

Break that and objects vanish into maps — stored under one hash, looked up
under another. Override the two together, always, or use a `record`, which
generates both correctly for free.

The reverse is not required: equal hashes for unequal objects is a collision,
which is fine and handled.

A mutable key whose hash changes after insertion is lost in the same way, which
is why immutable keys are the rule.

## Useful Map methods

```java
map.getOrDefault(k, 0)
map.putIfAbsent(k, v)
map.computeIfAbsent(k, key -> new ArrayList<>()).add(item)
map.merge(k, 1, Integer::sum)        // the counting idiom
```

(Calls on some `map`.) What each does:

- `getOrDefault(k, 0)` returns the value for `k`, or `0` if there is none,
  instead of `null`.
- `putIfAbsent(k, v)` stores `v` only if `k` has no value yet.
- `computeIfAbsent(k, f)` returns the value for `k`; if there is none, it
  first calls `f` to make one and stores it. Grouping items into lists is the
  classic use: the list is created the first time a key is seen.
- `merge(k, 1, Integer::sum)` stores `1` if `k` is new, and otherwise
  replaces the old value with `Integer.sum(old, 1)`. `Integer::sum` is a
  **method reference**, a short way of passing the method `Integer.sum` as a
  function (the Lambdas lesson).

`computeIfAbsent` for grouping and `merge` for counting replace most of the
if-then-put code people still write. Counting the old way, for comparison:

```java
Integer old = counts.get(word);
if (old == null) {
    counts.put(word, 1);
} else {
    counts.put(word, old + 1);
}
```

The single `merge` line says the same thing with none of the ceremony, and
cannot get the `null` case wrong.

## Run

```java
import java.util.*;

public class CollectionsDemo {
    static class BadKey {
        final String id;
        BadKey(String id) { this.id = id; }
        @Override public boolean equals(Object o) { return o instanceof BadKey b && b.id.equals(id); }
        // no hashCode: equal keys get different hashes
    }

    record GoodKey(String id) {}

    public static void main(String[] args) {
        Set<BadKey> bad = new HashSet<>();
        bad.add(new BadKey("a"));
        Set<GoodKey> good = new HashSet<>();
        good.add(new GoodKey("a"));
        System.out.println(bad.contains(new BadKey("a")) + " " + good.contains(new GoodKey("a")));

        Map<String, Integer> counts = new TreeMap<>();
        for (String w : "b a b c b".split(" ")) counts.merge(w, 1, Integer::sum);
        System.out.println(counts);

        Map<Integer, List<String>> byLength = new LinkedHashMap<>();
        for (String w : List.of("kiwi", "fig", "pear")) {
            byLength.computeIfAbsent(w.length(), k -> new ArrayList<>()).add(w);
        }
        System.out.println(byLength);
    }
}
```

```output
false true
{a=1, b=3, c=1}
{4=[kiwi, pear], 3=[fig]}
```

`BadKey` overrides `equals` but not `hashCode`, so two equal keys get
different hashes (the default `hashCode` comes from object identity). The set
looks in the wrong bucket and reports `false` for a key that is, by
`equals`, right there. The record generates both, so `GoodKey` works. The
`TreeMap` prints its keys sorted, whatever order they were counted in. The
`LinkedHashMap` keeps the order keys were first added: 4 (from `kiwi`) before
3 (from `fig`).

## Your turn

In `Store.java`:

- `public static Map<String, Integer> countWords(String text)` — how many
  times each word appears, lower-cased, splitting on any run of whitespace:
  `"The the THE"` gives `{the=3}`, extra spaces make no difference, and an
  empty string gives an empty map (`"".split(...)` gives one empty string,
  which must not be counted as a word)
- `public static String firstUnique(String text)` — the first word, in the
  order of the text, that appears exactly once, or `null` if every word
  repeats: in `"the cat the dog"` it is `"cat"`
- `public static List<Map.Entry<String, Integer>> sortedByValue(Map<String, Integer> counts)`
  — the map's entries as a list, count descending, then key ascending for
  equal counts. `Map.Entry.comparingByValue()` and `comparingByKey()` give
  ready-made comparators, and `reversed()` and `thenComparing(...)` combine
  them.
- `public static List<String> dedupe(List<String> items)` — the items without
  duplicates, in first-seen order: `{b, a, b, c, a}` gives `[b, a, c]`
