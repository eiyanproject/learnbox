---
title: Implementing iterators
summary: Write your own Iterator, make a collection work in for loops with IntoIterator, and add adapter methods with an extension trait.
order: 4
files: [src/lib.rs]
run: cargo test
hints:
  - "`Fibonacci` stores `(curr, next)`; `next()` uses `checked_add` and returns `None` once the sum would overflow `u64`, so the iterator ends instead of panicking."
  - "`Countdown`'s `next` returns `Some` of the current value and decrements; it also implements `DoubleEndedIterator` with a separate `front` and `back`."
  - "`impl<'a, T> IntoIterator for &'a Ring<T> { type Item = &'a T; type IntoIter = std::slice::Iter<'a, T>; fn into_iter(self) -> Self::IntoIter { self.items.iter() } }`."
  - "The extension trait: `pub trait EveryNth: Iterator + Sized { fn every_nth(self, n: usize) -> EveryNthIter<Self> { EveryNthIter { inner: self, n, i: 0 } } }` and `impl<I: Iterator> EveryNth for I {}`."
---

Anything with a `next` method returning `Option<Item>` is an iterator, and
implementing that one method gives you every adapter in the standard library
for free: `map`, `filter`, `take`, `zip`, `sum`, `collect`...

## Implementing Iterator

```rust
pub struct Squares {
    n: u32,
}

impl Iterator for Squares {
    type Item = u32;

    fn next(&mut self) -> Option<u32> {
        self.n += 1;
        Some(self.n * self.n)       // an infinite iterator
    }
}

let v: Vec<u32> = Squares { n: 0 }.take(3).collect();   // [1, 4, 9]
```

Returning `None` ends the iteration. An iterator may be infinite; the caller
decides how much to take.

## Iterating both ways and knowing the length

Optional traits unlock more adapters:

- `DoubleEndedIterator` (`next_back`) enables `.rev()` and taking from the end.
- `ExactSizeIterator` (`len`) when the remaining count is known exactly.
- Overriding `size_hint` helps `collect` allocate once.

## IntoIterator: making for loops work

`for x in thing` calls `IntoIterator::into_iter(thing)`. For a collection, you
usually provide three impls, matching `Vec`:

```rust
for x in v        // Vec<T>:     yields T,       consumes v
for x in &v       // &Vec<T>:    yields &T
for x in &mut v   // &mut Vec<T>: yields &mut T
```

The borrowed versions usually delegate to an inner slice iterator:

```rust
impl<'a, T> IntoIterator for &'a Ring<T> {
    type Item = &'a T;
    type IntoIter = std::slice::Iter<'a, T>;
    fn into_iter(self) -> Self::IntoIter {
        self.items.iter()
    }
}
```

## Extension traits: adding adapters

You cannot add methods to `Iterator` itself, but you can define a trait with a
default method and implement it for **all** iterators:

```rust
pub trait Pairs: Iterator + Sized {
    fn pairs(self) -> PairsIter<Self> {
        PairsIter { inner: self }
    }
}

impl<I: Iterator> Pairs for I {}
```

Now every iterator has `.pairs()`. This is how crates like `itertools` extend
the standard library.

## Laziness

Adapters build nested structs; nothing runs until something calls `next`. A
long chain compiles down to roughly the same machine code as a hand-written
loop.

## Your turn

In `src/lib.rs`:

- `Fibonacci::new()`: yields `0, 1, 1, 2, 3, ...` and **ends** (returns `None`)
  instead of overflowing `u64`
- `Countdown::new(n)`: yields `n, n-1, ..., 1`; also implements
  `DoubleEndedIterator` so `.rev()` counts up, and reports an exact `size_hint`
- `Ring<T>`: a wrapper over `Vec<T>`; `for x in &ring` yields `&T`, and
  `for x in ring` yields `T`
- `EveryNth` extension trait: `.every_nth(n)` yields items at positions 0, n, 2n, ...
