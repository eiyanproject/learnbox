---
title: Iterators and ranges
summary: The half-open range every algorithm takes, what invalidates an iterator, and the C++20 syntax that takes the container instead.
order: 4
files: [ranges.h]
run: g++ -std=c++20 -Wall -fsyntax-only ranges.h && echo "header compiles"
hints:
  - "`sum_range` takes two iterators and adds everything in [first, last) - note the end is not included, which is what makes end() work."
  - "`remove_all` needs the erase-remove idiom: `v.erase(std::remove(v.begin(), v.end(), value), v.end())`. std::remove alone does not shorten the vector."
  - "`evens_doubled` can use a ranges pipeline: `v | std::views::filter(...) | std::views::transform(...)` and then build a vector from it."
  - "Build the vector from a view with a loop or std::ranges::copy - ranges::to is C++23 and this is C++20."
---

Every standard algorithm takes a **range** as two iterators: the first element,
and one **past** the last.

```cpp
std::sort(v.begin(), v.end());
```

## Why half-open

`[first, last)` — the end is not included. Three consequences that all fall out
of the same choice:

- `last - first` is the size, with no off-by-one.
- An empty range is `first == last`, which needs no special case.
- `end()` can be a real position: one past the last element, which always
  exists as an address even though it holds nothing.

This is the same convention as `substring(a, b)` in Java and slicing in Python.

## The categories

| | Can do |
|---|---|
| Input / Output | read or write once, forward |
| Forward | multi-pass, forward |
| Bidirectional | `--` as well — `std::list`, `std::map` |
| Random access | `+ n` in constant time — `vector`, `array` |

`std::sort` requires random access, which is why you cannot sort a
`std::list` with it — the list has its own `sort` member.

## Invalidation

```cpp
auto it = v.begin();
v.push_back(1);      // it may now be dangling
*it;                 // undefined behaviour
```

Any reallocation invalidates every iterator into a `vector`. Erasing
invalidates from the erased position onwards. The rules differ per container,
and the safe habit is to re-obtain iterators after modifying a container rather
than to memorise them.

## The erase-remove idiom

```cpp
v.erase(std::remove(v.begin(), v.end(), value), v.end());
```

`std::remove` cannot change the container's size — it only has iterators, not
the container. It shuffles the survivors forward and returns the new logical
end; `erase` then actually shortens it. Calling `remove` alone leaves the
vector the same length with stale values at the back, which is a genuinely
confusing first encounter.

C++20 adds `std::erase(v, value)` as a free function that does both.

## Ranges

```cpp
std::ranges::sort(v);                          // takes the container
auto evens = v | std::views::filter(is_even);  // lazy, composable
```

Views are lazy and cheap to copy: nothing happens until iterated, and nothing
is allocated.

## Your turn

In `ranges.h`:

- `template <typename It> auto sum_range(It first, It last)`
- `void remove_all(std::vector<int>& values, int value)` — erase-remove
- `std::vector<int> evens_doubled(const std::vector<int>& values)`
- `std::size_t count_between(const std::vector<int>& values, int lo, int hi)` —
  inclusive
