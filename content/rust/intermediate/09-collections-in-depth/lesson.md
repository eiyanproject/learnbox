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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **`std::collections`** | the standard library's collection types |
| **hash** | a number worked out from a key, used to jump to its slot |
| **`Hash + Eq`** | what `HashMap` and `HashSet` keys must implement |
| **`Ord`** | full ordering; what `BTreeMap` and `BTreeSet` keys must implement |
| **`BTreeMap`** / **`BTreeSet`** | keys kept sorted in a tree; iterate in order, ask for ranges |
| **set** | each value at most once |
| **union** / **intersection** | everything in either / only what is in both |
| **difference** / **symmetric difference** | in the first but not the second / in exactly one |
| **de-duplication** | building a set from a list keeps one of each |
| **priority queue** | always gives the most important item next |
| **`BinaryHeap`** | a max-heap: `pop` returns the largest item |
| **`Reverse`** | a wrapper that flips comparison, turning a max-heap into a min-heap |
| **tuple ordering** | tuples compare field by field, left to right |
| **`VecDeque`** | a double-ended queue: fast at both ends |
| **queue** (FIFO) | first in, first out |
| **graph** | nodes connected by edges |
| **undirected edge** | can be followed both ways |
| **breadth-first search** (BFS) | explore nearest first, level by level; finds shortest paths |
| **visited set** | the nodes already seen, so the search does not go in circles |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `use std::collections::{BTreeMap, HashSet, BinaryHeap, VecDeque, HashMap};` | brings them in |
| `map.range("2026-01".."2026-02")`, `map.iter().rev()` | a range of keys; largest first |
| `a.union(&b)`, `a.intersection(&b)`, `a.difference(&b)`, `a.symmetric_difference(&b)` | set operations, as iterators of references |
| `.copied()`, `.cloned()` | owned values from references |
| `HashSet::from([1, 2, 3])`, `[1, 2, 3].into()` | a set from an array |
| `heap.push(x)`, `heap.pop()` | add; take the largest |
| `std::cmp::Reverse(x)` | flips the order |
| `heap.push((count, Reverse(word)))` | highest count first, then alphabetical |
| `queue.push_back(x)`, `queue.pop_front()` | use a `VecDeque` as a queue |
| `std::iter::from_fn(\|\| heap.pop())` | an iterator from a closure |
| `usize::MAX` | used as "not seen yet" |

### Errors

| Error | Means |
|---|---|
| `the trait bound MyType: Ord is not satisfied` | a `BTreeMap` key without `Ord` |
| `the trait bound MyType: Hash is not satisfied` | a `HashMap` key without `Hash` |

---

Beginner lesson 9 covered `Vec`, `String` and `HashMap`, which handle most
needs. The standard library's `std::collections` has a few more, each built
for one job that the big three do badly. Choosing the right one often turns
a slow, fiddly function into a few lines, and this lesson's exercise is four
problems, each with the collection that fits it.

## The standard collections at a glance

| Need | Use | Why not the obvious choice? |
|---|---|---|
| a list, add and remove at the end | `Vec<T>` | |
| add at one end, remove at the other (a queue) | `VecDeque<T>` | `Vec::remove(0)` shifts every other item along |
| look up by key, order does not matter | `HashMap<K, V>` | |
| look up by key, **walk in key order**, find key ranges | `BTreeMap<K, V>` | a `HashMap` has no order at all |
| "is it in there?", no duplicates | `HashSet<T>` / `BTreeSet<T>` | a `Vec` must check every item |
| repeatedly take the **largest** item | `BinaryHeap<T>` | re-sorting a `Vec` after every insert is slow |

The two families of maps and sets make different demands on the key type:

- `HashMap` and `HashSet` need keys that are `Hash + Eq`: they work out a
  number from each key, its **hash**, and use it to jump straight to the
  key's slot. They are usually the fastest, and have no order.
- `BTreeMap` and `BTreeSet` need keys that are `Ord`: they keep keys in a
  sorted tree, so lookups are a little slower (about one comparison per
  level of the tree), but iteration is always in key order and you can ask
  for a range of keys.

Strings, integers, `char`, `bool`, and tuples of those, satisfy both. For your
own types, `#[derive(PartialEq, Eq, Hash)]` or `#[derive(PartialEq, Eq,
PartialOrd, Ord)]` provide what is needed.

## BTreeMap: a map that stays sorted

```rust
use std::collections::BTreeMap;

let mut by_date = BTreeMap::new();
by_date.insert("2026-09-18", "deploy");
by_date.insert("2026-01-02", "kickoff");
for (date, event) in &by_date { }          // in date order, whatever the insert order
by_date.range("2026-06-01"..)               // the entries from that key onwards
by_date.first_key_value()                   // Some((smallest key, its value))
```

(A fragment.) Dates written as `YYYY-MM-DD` sort correctly as plain strings,
which is why that format is popular. `range` takes the same ranges as
slicing: `a..b`, `a..`, `..=b`. Iterating backwards, `.iter().rev()`,
gives the largest key first, which is how you get "highest score first" in
the exercise. The API otherwise matches `HashMap`: `insert`, `get`,
`entry`, `remove`.

## Set algebra

A set holds each value at most once. Besides fast "is it in there?"
(`contains`), sets support the classic operations of set theory:

```rust
use std::collections::HashSet;

let a: HashSet<i32> = [1, 2, 3].into();
let b: HashSet<i32> = [2, 3, 4].into();
a.intersection(&b)           // in both:          2, 3
a.union(&b)                  // in either:        1, 2, 3, 4
a.difference(&b)             // in a but not b:   1
a.symmetric_difference(&b)   // in exactly one:   1, 4
a.is_subset(&b)              // is every item of a also in b? false
```

(A fragment.) As a picture, with `a` holding 1, 2, 3 and `b` holding 2, 3, 4:

```text
   only in a      in both      only in b
       1           2, 3            4
   difference   intersection
   └───── symmetric difference: 1 and 4 ─────┘
   └──────────── union: all four ────────────┘
```

`[1, 2, 3].into()` builds a set from an array, through the `From` trait
(lesson 3). Building one from a slice with duplicates, such as
`["rust", "web", "rust"]`, silently keeps one `"rust"`: that de-duplication
is half of the exercise's tag functions. The operations return **iterators
of references** into the sets, in no particular order; add `.copied()` (for
`Copy` items) or `.cloned()` to get owned values, then `collect` and `sort`
for a stable order.

## BinaryHeap: a priority queue

A **priority queue** is a collection where you can always take out the most
important item next, however many you add in between: the next job to run,
the closest unexplored location, the most frequent word. `BinaryHeap` is a
**max**-heap: `pop` always returns the largest item. Both `push` and `pop`
are fast, much faster than sorting everything each time.

```rust
use std::collections::BinaryHeap;
use std::cmp::Reverse;

let mut heap = BinaryHeap::new();
heap.push(5);
heap.push(1);
heap.push(8);
heap.pop()                  // Some(8), then Some(5), then Some(1), then None

let mut min_heap = BinaryHeap::new();
min_heap.push(Reverse(5));  // Reverse flips the ordering: the smallest comes out first
```

(A fragment.) `std::cmp::Reverse` is a wrapper whose comparison is the
opposite of what it wraps: `Reverse(1) > Reverse(5)`. The heap still takes
the "largest", which is now the smallest number.

Priorities with several parts use **tuples**, which compare field by field,
left to right: the first fields decide, and only on a tie does the second
field matter. So a heap of `(count, Reverse(word))` gives the highest count
first, and among equal counts the alphabetically **first** word, because
`Reverse` flips `"a" < "b"` into `Reverse("a") > Reverse("b")`. That is
exactly what `top_k_frequent` needs.

## VecDeque and breadth-first search

A `VecDeque` ("vec-deck", a double-ended queue) can add and remove at
**both** ends quickly: `push_back`, `push_front`, `pop_back`, `pop_front`.
Used with `push_back` and `pop_front` only, it is a **queue**: first in,
first out, like a line at a counter.

The classic use is **breadth-first search** (BFS): exploring a graph of
connected nodes, nearest first. Start from one node; visit all its
neighbours (distance 1); then all of *their* unvisited neighbours (distance
2); and so on, like ripples spreading on water. Because nodes are taken out
in the order they were found, every node is first reached by a shortest
route, so BFS finds shortest paths in graphs where every edge counts the
same:

```rust
use std::collections::VecDeque;

let mut queue = VecDeque::new();
queue.push_back(start);
while let Some(node) = queue.pop_front() {
    for next in neighbours(node) {
        // only if next has not been seen before:
        queue.push_back(next);
    }
}
```

(A sketch.) You must remember which nodes have been seen already, in a
`HashSet` or an array, and only queue unseen ones. Otherwise two nodes that
point at each other send the search round in circles forever.

## Run it

```rust
use std::cmp::Reverse;
use std::collections::{BTreeMap, BinaryHeap, HashSet, VecDeque};

fn main() {
    let mut by_date = BTreeMap::new();
    by_date.insert("2026-09-18", "deploy");
    by_date.insert("2026-01-02", "kickoff");
    by_date.insert("2026-07-04", "review");
    println!("{:?}", by_date.values().collect::<Vec<_>>());
    println!("{:?}", by_date.range("2026-06-01"..).map(|(_, e)| *e).collect::<Vec<_>>());
    println!("{:?}", by_date.first_key_value());

    let a: HashSet<i32> = [1, 2, 3].into();
    let b: HashSet<i32> = [2, 3, 4].into();
    let mut both: Vec<i32> = a.intersection(&b).copied().collect();
    let mut either: Vec<i32> = a.symmetric_difference(&b).copied().collect();
    both.sort();                      // a HashSet has no order: sort to compare
    either.sort();
    println!("{both:?} {either:?} {}", a.is_subset(&b));

    let mut heap = BinaryHeap::from([5, 1, 8]);
    let mut min_heap = BinaryHeap::from([Reverse(5), Reverse(1), Reverse(8)]);
    println!("{:?} {:?}", heap.pop(), min_heap.pop().map(|Reverse(x)| x));

    let mut tasks = BinaryHeap::from([(2, Reverse("b")), (3, Reverse("z")), (2, Reverse("a"))]);
    let order: Vec<&str> = std::iter::from_fn(|| tasks.pop().map(|(_, Reverse(n))| n)).collect();
    println!("{order:?}");

    // breadth-first distances in a small graph: 0 -> 1, 2; 1 -> 3; 2 -> 3
    let edges: [Vec<usize>; 4] = [vec![1, 2], vec![3], vec![3], vec![]];
    let mut dist = [usize::MAX; 4];
    dist[0] = 0;
    let mut queue = VecDeque::from([0]);
    while let Some(node) = queue.pop_front() {
        for &next in &edges[node] {
            if dist[next] == usize::MAX {
                dist[next] = dist[node] + 1;
                queue.push_back(next);
            }
        }
    }
    println!("{dist:?}");
}
```

```output
["kickoff", "review", "deploy"]
["review", "deploy"]
Some(("2026-01-02", "kickoff"))
[2, 3] [1, 4] false
Some(8) Some(1)
["z", "a", "b"]
[0, 1, 1, 2]
```

The map printed in date order although `deploy` was inserted first. In the
task heap, `z` comes first on priority 3; then, on equal priority 2,
`Reverse` puts `a` ahead of `b`. (`std::iter::from_fn` makes an iterator
from a closure, calling it until it returns `None`: a short way to pop
everything.)

The BFS used `usize::MAX` as "not seen yet". Node 3 is reachable both via 1
and via 2; it was first found from node 1, with distance 2, and the second
route was ignored because `dist[3]` was already set:

| Queue before | Take | New neighbours | `dist` after |
|---|---|---|---|
| `[0]` | 0 | 1, 2 | `[0, 1, 1, MAX]` |
| `[1, 2]` | 1 | 3 | `[0, 1, 1, 2]` |
| `[2, 3]` | 2 | none (3 already seen) | same |
| `[3]` | 3 | none | same |

## Your turn

In `src/lib.rs`, each function with the collection named:

- `leaderboard(scores: &[(&str, u32)])`, with `BTreeMap`: one line per
  score, formatted `"90: ana, budi"`, highest score first, the names for each
  score sorted alphabetically and joined by `", "`. An empty list gives an
  empty `Vec`.
- `common_tags(a, b)` and `unique_to_first(a, b)`, with `HashSet`: the tags in
  both lists, and the tags in `a` but not in `b`. Each tag appears once even if
  a list repeats it, and the result is sorted: with `a = ["rust", "web",
  "cli", "rust"]` and `b = ["cli", "python", "rust"]`, they are
  `["cli", "rust"]` and `["web"]`.
- `top_k_frequent(words, k)`, with `BinaryHeap`: the `k` most frequent words,
  most frequent first; among words with the same count, alphabetical order.
  If there are fewer than `k` different words, return them all.
- `shortest_path(edges, start, goal)`, with `VecDeque`: the number of edges
  on the shortest path from `start` to `goal`, or `None` if there is none.
  The graph is given as pairs and is **undirected**: `("a", "b")` lets you go
  from `a` to `b` and from `b` to `a`, so build a map of neighbours with
  both directions first. `start == goal` is `Some(0)`, and a node that does
  not appear in any edge cannot be reached.
