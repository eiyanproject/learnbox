---
title: Collections in depth
summary: BTreeMap for ordered keys, HashSet algebra, BinaryHeap priority queues, VecDeque, and choosing the right one.
order: 9
files: [src/lib.rs]
run: cargo test
hints:
  - "`leaderboard`: `BTreeMap<u32, Vec<String>>` keyed by score; `.iter().rev()` walks from the highest score. Sort names inside each bucket."
  - "`common_tags` and `unique_to_first`: build `HashSet<&str>`s, then `a.intersection(&b)` and `a.difference(&b)`, collect and sort."
  - "`top_k_frequent`: count with a `HashMap`, collect `(count, Reverse(word))` pairs into a `BinaryHeap`, and `pop` up to k times. `Reverse` flips the word ordering, so equal counts come out alphabetically."
  - "`shortest_path` is breadth-first search: `VecDeque` of `(node, distance)`, a `HashSet` of visited nodes, `pop_front`, and push unvisited neighbours with `distance + 1`."
---

## The standard collections at a glance

| Need | Use |
|---|---|
| a list, push/pop at the end | `Vec<T>` |
| push/pop at **both** ends (a queue) | `VecDeque<T>` |
| look up by key, order does not matter | `HashMap<K, V>` |
| look up by key, **iterate in key order**, ranges | `BTreeMap<K, V>` |
| membership, no duplicates | `HashSet<T>` / `BTreeSet<T>` |
| repeatedly take the **largest** item | `BinaryHeap<T>` |

`Hash*` collections need `K: Hash + Eq` and are usually fastest. `BTree*`
collections need `K: Ord`, keep keys sorted, and support `range(..)`.

## BTreeMap

```rust
use std::collections::BTreeMap;

let mut by_date = BTreeMap::new();
by_date.insert("2026-09-18", "deploy");
by_date.insert("2026-01-02", "kickoff");
for (date, event) in &by_date { }          // in date order
by_date.range("2026-06-01"..)               // everything from June on
by_date.first_key_value()                   // the smallest key
```

## Set algebra

```rust
use std::collections::HashSet;

let a: HashSet<i32> = [1, 2, 3].into();
let b: HashSet<i32> = [2, 3, 4].into();
a.intersection(&b)           // 2, 3
a.union(&b)                  // 1, 2, 3, 4
a.difference(&b)             // 1
a.symmetric_difference(&b)   // 1, 4
a.is_subset(&b)
```

These return iterators of references; `.copied().collect()` or `.cloned()` to own them.

## BinaryHeap: a priority queue

`BinaryHeap` is a **max**-heap: `pop` always returns the largest item.

```rust
use std::collections::BinaryHeap;
use std::cmp::Reverse;

let mut heap = BinaryHeap::new();
heap.push(5); heap.push(1); heap.push(8);
heap.pop()                  // Some(8)

let mut min_heap = BinaryHeap::new();
min_heap.push(Reverse(5));  // Reverse flips the ordering: smallest comes out first
```

Tuples compare field by field, so `(priority, Reverse(name))` means "highest
priority first, and alphabetical among equals".

## VecDeque and breadth-first search

```rust
use std::collections::VecDeque;

let mut queue = VecDeque::new();
queue.push_back(start);
while let Some(node) = queue.pop_front() {
    for next in neighbours(node) {
        queue.push_back(next);
    }
}
```

Exploring a graph in order of distance from the start (BFS) finds shortest
paths in unweighted graphs.

## Your turn

In `src/lib.rs`:

- `leaderboard(scores: &[(&str, u32)])`: lines like `"90: ana, budi"`, highest
  score first, names sorted within a score, using `BTreeMap`
- `common_tags(a, b)` and `unique_to_first(a, b)`: sorted, de-duplicated, using `HashSet` operations
- `top_k_frequent(words, k)`: the `k` most frequent words, ties broken
  alphabetically, using `BinaryHeap`
- `shortest_path(edges, start, goal)`: number of edges on the shortest path in
  an undirected graph given as pairs, or `None` if unreachable (BFS with `VecDeque`)
