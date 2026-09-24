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

Three interfaces cover nearly everything:

| | Holds | |
|---|---|---|
| `List` | ordered, duplicates allowed | index access |
| `Set` | no duplicates | membership |
| `Map` | key to value | lookup by key |

`Queue` and `Deque` add ends-based access. `Collection` is the parent of the
first two; `Map` is deliberately **not** a `Collection`.

## Choosing an implementation

| Need | Use | Why |
|---|---|---|
| a general list | `ArrayList` | O(1) index, cheap iteration |
| lots of insertion at the ends | `LinkedList` / `ArrayDeque` | no shifting |
| a plain set | `HashSet` | O(1), no order |
| insertion order kept | `LinkedHashSet` / `LinkedHashMap` | predictable output |
| sorted order | `TreeSet` / `TreeMap` | O(log n), needs ordering |
| a stack or queue | `ArrayDeque` | faster than `Stack`, which is legacy |

`ArrayList` beats `LinkedList` in almost every real case, including removal,
because cache locality outweighs the pointer arithmetic. `LinkedList` is on the
exam far more than it should be in your code.

## equals and hashCode

A `HashSet` or `HashMap` finds an object by its hash first. So:

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

`computeIfAbsent` for grouping and `merge` for counting replace most of the
if-then-put code people still write.

## Your turn

In `Store.java`:

- `public static Map<String, Integer> countWords(String text)` — lowercase,
  split on whitespace
- `public static String firstUnique(String text)` — the first word appearing
  once, or `null`
- `public static List<Map.Entry<String, Integer>> sortedByValue(Map<String, Integer> counts)`
  — count descending, then key ascending
- `public static List<String> dedupe(List<String> items)` — first-seen order
