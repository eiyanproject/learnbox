---
title: A container with iterators
summary: A fixed-capacity ring buffer that works with range-for and the standard algorithms, because it provides the five things an iterator has to provide.
order: 1
files: [ring.h]
run: g++ -std=c++20 -Wall -fsyntax-only ring.h && echo "header compiles"
hints:
  - "Store a std::array<T, N> plus head_ (index of the oldest element) and size_. push writes at (head_ + size_) % N; when the buffer is full it also advances head_."
  - "operator[](i) is the i-th *oldest* element: data_[(head_ + i) % N]."
  - "The iterator needs the five member typedefs (iterator_category, value_type, difference_type, pointer, reference) or std::iterator_traits cannot describe it and the algorithms will not compile."
  - "Give the iterator a logical position 0..size_ rather than a raw pointer - a pointer cannot express the wrap, and end() would be ambiguous with begin() on a full buffer."
---

A container is not a container to the standard library until it hands out
iterators. Once it does, `for (x : c)`, `std::find`, `std::ranges::count` and
everything else work on it for free.

## The ring

Fixed capacity `N`. `push` appends; when it is full, the oldest element is
overwritten. Two integers describe the state:

```
data_ :  [ c ][ d ][ _ ][ a ][ b ]
                        head_=3, size_=4
logical order: a b c d
```

The physical index of logical element `i` is `(head_ + i) % N`. Every operation
is that one expression.

## What range-for actually needs

```cpp
for (int x : ring) { ... }
```

desugars to roughly

```cpp
auto it = ring.begin();
auto stop = ring.end();
for (; it != stop; ++it) { int x = *it; ... }
```

So the minimum is `begin()`, `end()`, `operator*`, `operator++` and
`operator!=`. That is all range-for asks for.

## What the algorithms need

More. `std::iterator_traits<It>` has to be able to answer five questions, and
it answers them by looking for five member typedefs:

```cpp
using iterator_category = std::forward_iterator_tag;
using value_type        = T;
using difference_type   = std::ptrdiff_t;
using pointer           = const T*;
using reference         = const T&;
```

Leave these out and `std::find(r.begin(), r.end(), 3)` fails to compile with an
error that is famously unhelpful. The category is a promise: a forward iterator
can be copied and re-traversed, which a plain input iterator cannot.

## Position, not pointer

The obvious implementation is a `T*` walking the array — and it is wrong here.
On a full buffer the last element wraps around to sit *before* the first, so a
pointer at "one past the end" would equal `begin()`. Carrying a logical index
`0..size_` instead makes `end()` unambiguous.

This is the same reason `std::deque`'s iterator is not a pointer.

## Your turn

In `ring.h`, `template <typename T, std::size_t N> class Ring`:

- `push(const T&)`, `size()`, `empty()`, `full()`, `capacity()`
- `front()` (oldest) and `back()` (newest)
- `operator[](std::size_t)`, const and non-const, oldest-first
- a nested `const_iterator`, plus `begin() const` and `end() const`
