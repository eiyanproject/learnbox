---
title: Implementing iterators
summary: Write your own Iterator, make a collection work in for loops with IntoIterator, and add adapter methods with an extension trait.
order: 4
files: [src/lib.rs]
run: cargo test
hints:
  - "`Fibonacci` stores the current value and the next one, both as `Option<u64>`. `next()` hands out the current value, then moves along, computing the one after with `checked_add`; once that overflows it is `None`, and the iterator ends after the values it still holds."
  - "`Countdown` keeps a `front` (starting at `n`) and a `back` (starting at 1). `next` takes from the front and decrements it, `next_back` takes from the back and increments it, and both stop when `front < back`. `size_hint` is `front - back + 1`, or 0."
  - "`impl<'a, T> IntoIterator for &'a Ring<T> { type Item = &'a T; type IntoIter = std::slice::Iter<'a, T>; fn into_iter(self) -> Self::IntoIter { self.items.iter() } }`. The owned version uses `std::vec::IntoIter<T>` and `self.items.into_iter()`."
  - "The extension trait: `pub trait EveryNth: Iterator + Sized { fn every_nth(self, n: usize) -> EveryNthIter<Self> { EveryNthIter { inner: self, n, i: 0 } } }` and `impl<I: Iterator> EveryNth for I {}`."
---

Beginner lesson 11 used iterators; this lesson writes them. The reward is
large: implement **one** method, `next`, and your type gets every adapter
and consumer in the standard library (`map`, `filter`, `take`, `zip`, `sum`,
`collect` and dozens more) without writing any of them. The same idea then
works in two more directions: making your own collection usable in `for`
loops, and adding new adapter methods to *every* iterator.

## Implementing Iterator

An iterator is a struct that remembers where it is, plus an `impl Iterator`
saying how to produce the next value:

```rust
pub struct Squares {
    n: u32,
}

impl Iterator for Squares {
    type Item = u32;

    fn next(&mut self) -> Option<u32> {
        self.n += 1;
        Some(self.n * self.n)       // never None: an infinite iterator
    }
}

let v: Vec<u32> = Squares { n: 0 }.take(3).collect();   // [1, 4, 9]
```

(A fragment.) The pieces:

- `type Item = u32;` is the associated type (lesson 3): what this iterator
  produces.
- `next` takes `&mut self` because producing a value changes the position:
  the iterator **is** its own cursor. That is also why `let mut it = ...;` is
  needed to call `it.next()` by hand.
- `next` returns `Some(value)` while there are values, and `None` to say "no
  more". Once an iterator has returned `None`, callers stop asking, and most
  code assumes it would keep saying `None`.

`Squares` never returns `None`, so it is **infinite**. That is allowed and
useful: the caller decides how much to take, with `take(3)` or
`take_while(...)`. Calling `collect()` or `sum()` on an infinite iterator
directly would loop forever.

Step by step, `Squares { n: 0 }.take(3).collect()`:

| `collect` asks `take` | `take` has given | `take` asks `Squares` | `n` becomes | gives |
|---|---|---|---|---|
| 1st | 0 | yes | 1 | `Some(1)` |
| 2nd | 1 | yes | 2 | `Some(4)` |
| 3rd | 2 | yes | 3 | `Some(9)` |
| 4th | 3: limit reached | no | 3 | `None` |

`take` stops asking once it has given three, so `Squares` is only run three
times.

### Ending an iterator: the overflow problem

A Fibonacci iterator (0, 1, 1, 2, 3, 5, ..., each the sum of the two before)
written the obvious way, `let next = a + b;`, works until the numbers no
longer fit in a `u64`. The 94th value is the largest that fits; computing
the next one overflows, which panics in a debug build. The fix is to make
the overflow the *end* of the sequence: `a.checked_add(b)` returns `None`
when the sum does not fit (Beginner lesson 2), and the iterator can
return `None` from that point on, after first handing out the values it
already holds.

## Iterating both ways and knowing the length

Two optional traits, implemented in addition to `Iterator`, unlock more
methods:

- `DoubleEndedIterator`, with one required method `next_back`, takes items
  from the **other end**. It is what `.rev()` needs: `rev` calls
  `next_back` whenever asked for `next`. Ranges and `Vec` iterators have it.
- `ExactSizeIterator`, for when the number of remaining items is known
  exactly. It gives `.len()`.

And one method of `Iterator` itself that is worth overriding:
`size_hint()` returns `(lower, Some(upper))`, the least and most items still
to come. The default is `(0, None)`, "no idea". `collect` uses it to
allocate the right amount of memory in one go. When you know the count
exactly, return it as both: `(n, Some(n))`.

With both ends in play, an iterator needs to know where *each* end is. Think
of a countdown from 4 as a row of numbers with a marker at each end:

```text
 start:            front=4  [4 3 2 1]  back=1
 next()      -> 4  front=3  [  3 2 1]
 next_back() -> 1           [  3 2  ]  back=2
 next()      -> 3  front=2  [    2  ]
 next_back() -> 2           [       ]  back=3      front < back: empty
 next()      -> None
```

The markers move towards each other, and when they cross, the iterator is
empty from both sides. The count of what is left is always
`front - back + 1` while `front >= back`, which is your `size_hint`.

## IntoIterator: making for loops work

A `for` loop does not take an iterator directly. `for x in thing` calls
`IntoIterator::into_iter(thing)` first, and loops over what that returns:

```rust
pub trait IntoIterator {
    type Item;
    type IntoIter: Iterator<Item = Self::Item>;
    fn into_iter(self) -> Self::IntoIter;
}
```

(Shortened.) Two associated types: the `Item` produced, and `IntoIter`, the
iterator type that produces it, which must be an `Iterator` with that same
`Item`. Every iterator implements `IntoIterator` by returning itself, which
is why `for n in 0..5` works. For a collection, you provide the impls, and
the convention is to match `Vec`, which has three:

```rust
for x in v        // IntoIterator for Vec<T>:      yields T,      consumes v
for x in &v       // IntoIterator for &Vec<T>:     yields &T,     borrows v
for x in &mut v   // IntoIterator for &mut Vec<T>: yields &mut T, borrows mutably
```

(Loop headers.) Each one is a separate `impl`, for the type, for a shared
reference to it, and for a mutable reference to it. This is what Beginner
lesson 4 meant by "loops move": `for x in v` uses the first impl, which
takes `v` by value.

For a wrapper type, the implementations usually **delegate**: hand the work
to the iterator of the collection inside. For the borrowed version:

```rust
impl<'a, T> IntoIterator for &'a Ring<T> {
    type Item = &'a T;
    type IntoIter = std::slice::Iter<'a, T>;

    fn into_iter(self) -> Self::IntoIter {
        self.items.iter()
    }
}
```

Reading it:

- `for &'a Ring<T>`: this impl is for a *reference* to a ring, valid for
  some lifetime `'a`. `self` is therefore a `&Ring<T>`.
- The items are `&'a T`: references into the ring, valid as long as the
  borrow of the ring (Beginner lesson 12).
- `self.items.iter()` already produces exactly those, and its type is
  `std::slice::Iter<'a, T>`, the standard iterator over a borrowed slice.
  The method's documentation lists that type; you do not need to write an
  iterator struct at all.

The owned version, `impl<T> IntoIterator for Ring<T>`, has `Item = T` and
delegates to `self.items.into_iter()`, whose type is `std::vec::IntoIter<T>`.

## Extension traits: adding adapters

You cannot add a method to the standard `Iterator` trait: it is not yours,
and editing it is not possible. You can, however, define your **own** trait
whose methods have default bodies, and implement it for every iterator with
one blanket impl (lesson 3). Every iterator then has your method. This is
called an **extension trait**:

```rust
pub struct PairsIter<I> {
    inner: I,
}

pub trait Pairs: Iterator + Sized {
    fn pairs(self) -> PairsIter<Self> {
        PairsIter { inner: self }
    }
}

impl<I: Iterator> Pairs for I {}
```

Three pieces, each with a job:

1. `PairsIter<I>` is the adapter itself: a struct that wraps any inner
   iterator `I`. Its own `impl Iterator` (in the program below) pulls two
   items from `inner` for each pair it produces.
2. `trait Pairs: Iterator + Sized` has a single default method, `pairs`,
   which wraps `self` in a `PairsIter`. The supertrait `Iterator` lets the
   wrapper treat `self` as an iterator.
3. `impl<I: Iterator> Pairs for I {}` is the blanket impl, with an empty
   body since the default is all we need. Every iterator, now and in the
   future, is a `Pairs`.

Why `+ Sized`? `pairs` takes `self` by value and stores it in a struct
field, so the compiler must know how big `self` is. A trait is normally
allowed to be implemented by types whose size is unknown at compile time
(such as `dyn Iterator` itself), so you have to promise the size is known.
Without it:

```text
error[E0277]: the size for values of type `Self` cannot be known at compilation time
  |
3 |     fn pairs(self) -> PairsIter<Self> {
  |                       ^^^^^^^^^^^^^^^ doesn't have a size known at compile-time
```

(The `help:` that follows suggests adding `where Self: Sized` to this one
method, which works too.) This is exactly how crates like `itertools` add
dozens of adapters to the standard library's iterators.

## Laziness, from the inside

Now it is visible why adapters are lazy: `.pairs()` does nothing but build a
`PairsIter` struct around the iterator. A chain like
`(1..=5).pairs().take(1)` builds a `Take<PairsIter<RangeInclusive<i32>>>`,
structs nested inside each other, and no item is produced until a consumer
calls the outermost `next`, which calls the next one in, and so on. The
compiler sees through all the nesting, and a long chain usually compiles to
the same machine code as a hand-written loop.

## Run it

```rust
struct Squares {
    n: u32,
}

impl Iterator for Squares {
    type Item = u32;
    fn next(&mut self) -> Option<u32> {
        self.n += 1;
        Some(self.n * self.n)
    }
}

struct PairsIter<I> {
    inner: I,
}

impl<I: Iterator> Iterator for PairsIter<I> {
    type Item = (I::Item, I::Item);
    fn next(&mut self) -> Option<Self::Item> {
        let a = self.inner.next()?;
        let b = self.inner.next()?;
        Some((a, b))
    }
}

trait Pairs: Iterator + Sized {
    fn pairs(self) -> PairsIter<Self> {
        PairsIter { inner: self }
    }
}

impl<I: Iterator> Pairs for I {}

fn main() {
    let v: Vec<u32> = Squares { n: 0 }.take(3).collect();
    println!("{v:?}");
    println!("{}", Squares { n: 0 }.filter(|x| x % 2 == 1).take(3).sum::<u32>());
    println!("{:?}", (1..=5).pairs().collect::<Vec<_>>());
    println!("{:?}", "abcd".chars().pairs().collect::<Vec<_>>());

    let mut it = (1..=4).rev();
    println!("{:?} {:?} {:?}", it.next(), it.next_back(), it.size_hint());
}
```

```output
[1, 4, 9]
35
[(1, 2), (3, 4)]
[('a', 'b'), ('c', 'd')]
Some(4) Some(1) (2, Some(2))
```

One `next`, and `take`, `filter`, `sum` and `collect` all came free: `35` is
1 + 9 + 25, the first three odd squares. `PairsIter::next` uses `?` on
`Option` (Beginner lesson 8): with `1..=5`, the third pair gets `5` and then
`None` for its second item, so it returns `None` and the lone `5` is
dropped. The last line shows a range taking from both ends, and its exact
`size_hint`: the pattern for `Countdown` below.

## Your turn

In `src/lib.rs`:

- `Fibonacci::new()`: yields `0, 1, 1, 2, 3, 5, 8, ...` (each value the sum
  of the two before), and **ends**, returning `None`, instead of overflowing
  `u64`. The tests collect the whole sequence and expect **94** values, the
  last one being 12200160415121876738, the largest Fibonacci number that
  fits. So when the *following* sum would overflow, the values already
  computed must still come out before the end.
- `Countdown::new(n)`: yields `n, n-1, ..., 1`, and nothing for `n = 0`.
  Also implement:
  - `DoubleEndedIterator`, so `.rev()` gives `1, 2, ..., n`, and `next` and
    `next_back` can be mixed, meeting in the middle as in the diagram above
  - an exact `size_hint`: after one `next` and one `next_back` on
    `Countdown::new(4)`, it is `(2, Some(2))`
- `Ring<T>`, a wrapper over `Vec<T>`: `for x in &ring` yields `&T` and leaves
  the ring usable; `ring.into_iter()` (or `for x in ring`) yields `T`
- an `EveryNth` extension trait: `.every_nth(n)` on any iterator yields the
  items at positions 0, n, 2n, ...: `(0..10).every_nth(3)` gives
  `[0, 3, 6, 9]`, and `every_nth(1)` gives everything. You write the
  `EveryNthIter` adapter struct and its `Iterator` impl too.
