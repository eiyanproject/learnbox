---
title: Advanced traits
summary: Generic associated types, impl Trait in traits, associated type bounds, and keeping a trait usable as dyn.
order: 9
files: [src/lib.rs]
run: cargo test
hints:
  - "`LendingIterator` has `type Item<'a> where Self: 'a;` and `fn next(&mut self) -> Option<Self::Item<'_>>`. `WindowsMut` yields `&'a mut [i32]` by reborrowing `&mut self.data[start..end]`."
  - "`Pipeline::steps(&self) -> impl Iterator<Item = &str>` is return-position impl Trait in a trait (RPITIT); `describe` is a default method built on it, `self.steps().collect::<Vec<_>>().join(\" -> \")`."
  - "`total_len<I>(items: I) where I: IntoIterator, I::Item: AsRef<str>`: an associated type bound, so the function accepts iterators of `&str`, `String`, or anything else viewable as text."
  - "`Repository` stays dyn-compatible by returning `Box<dyn Iterator<Item = String> + '_>` instead of `impl Iterator`, so `Vec<Box<dyn Repository>>` still works."
---

This lesson covers four trait features that recent Rust versions added or
completed, and that show up in modern library signatures:

1. **generic associated types** (GATs): an associated type with its own
   generic parameters, which makes "an iterator that lends out borrows of
   itself" expressible;
2. **`impl Trait` in traits**: a trait method returning "some iterator",
   without naming or boxing it;
3. **associated type bounds**: requirements on what an iterator yields,
   written where the iterator is accepted;
4. the cost of the first two: they can make a trait unusable as `dyn`, and
   how to design around that.

Each one is shown with the problem it solves, and the error you get without
it.

## The problem: an iterator that lends

Try to write an iterator over **overlapping mutable windows** of a vector:
`[1, 2]`, then `[2, 3]`, then `[3, 4]`, each one a `&mut [i32]` the caller
can change. The obvious `Iterator` impl does not compile:

```rust
impl Iterator for Windows {
    type Item = &mut [i32];
    fn next(&mut self) -> Option<Self::Item> { ... }
}
```

```text
error: associated type `Iterator::Item` is declared without lifetime parameters, so using a borrowed type for them requires that lifetime to come from the implemented type
  |
3 |     type Item = &mut [i32];
  |                 ^
  |
note: you can't create an `Iterator` that borrows each `Item` from itself, but you can instead create a new type that borrows your existing type and implement `Iterator` for that new type
```

And the version that borrows the data from outside, `WindowsMut<'a>` with
`type Item = &'a mut [i32]`, fails too:

```text
error: lifetime may not live long enough
  |
2 | impl<'a> Iterator for WindowsMut<'a> {
  |      -- lifetime `'a` defined here
...
4 |     fn next(&mut self) -> Option<&'a mut [i32]> {
  |             - let's call the lifetime of this reference `'1`
...
7 |         Some(w)
  |         ^^^^^^^ method was supposed to return data with lifetime `'a` but it is returning data with lifetime `'1`
```

This is not the compiler being fussy. `Iterator`'s contract is that items
are independent of the iterator and of each other: you may `collect()` them
all and hold them at once (Intermediate lesson 10). For overlapping mutable
windows that would mean two `&mut` to the same element at the same time,
exactly the aliasing that Rust forbids. What we want is a different
contract: **each item may borrow from the iterator, and must be given back
before the next one is taken**. That is called a **lending iterator**, and
expressing it needs the item type to depend on the lifetime of each `next`
call.

## Generic associated types

A **generic associated type** is an associated type with its own generic
parameters, here a lifetime:

```rust
pub trait LendingIterator {
    type Item<'a> where Self: 'a;
    fn next(&mut self) -> Option<Self::Item<'_>>;
}
```

Reading it:

- `type Item<'a>`: the item type is a family of types, one for each lifetime
  `'a`. An implementation sets, for example, `type Item<'a> = &'a mut [i32];`.
- `fn next(&mut self) -> Option<Self::Item<'_>>`: the `'_` is the lifetime
  of this call's `&mut self` borrow (elision rule 3). So the item borrows the
  iterator for as long as the caller holds the item.
- `where Self: 'a` says the iterator lives at least as long as `'a`, since an
  item cannot outlive what it borrows from. The compiler insists on this
  clause.

Because each item keeps the iterator mutably borrowed, calling `next` again
while the previous item is still in use is a borrow error, so overlapping
`&mut` windows can never exist at the same time, checked at compile time.
The usual way to drive one is `while let Some(item) = it.next() { ... }`:
each item is dropped at the end of the loop body, before the next call.

The price: none of `Iterator`'s adapters (`map`, `filter`, `collect`, `for`
loops) work, since they are defined on `Iterator`, whose contract this is
not. Lending iterators are for the cases that genuinely need them.

## impl Trait in traits

Since Rust 1.75, a trait method may return `impl Trait`, as an ordinary
function can:

```rust
pub trait Pipeline {
    fn steps(&self) -> impl Iterator<Item = &str>;

    fn describe(&self) -> String {
        self.steps().collect::<Vec<_>>().join(" -> ")
    }
}
```

(A fragment.) Each implementation returns its own concrete iterator type,
which is hidden from callers, so there is no `Box` and no allocation:
`Simple`'s implementation can return `self.steps.iter().map(|s| s.as_str())`
directly. Default methods such as `describe` can use it like any iterator.
This feature is often called **RPITIT** (return-position `impl Trait` in
traits).

The catch: the trait is no longer **dyn compatible** (Advanced lesson 10).
Each implementation's `steps` returns a different hidden type, of a
different size, so there is no single function signature to put in a
vtable:

```text
error[E0038]: the trait `Pipeline` is not dyn compatible
  |
4 | pub fn all(ps: &[Box<dyn Pipeline>]) -> usize { ps.len() }
  |                      ^^^^^^^^^^^^ `Pipeline` is not dyn compatible
  |
note: for a trait to be dyn compatible it needs to allow building a vtable
  |
1 | pub trait Pipeline {
  |           -------- this trait is not dyn compatible...
2 |     fn steps(&self) -> impl Iterator<Item = &str>;
  |                        ^^^^^^^^^^^^^^^^^^^^^^^^^^ ...because method `steps` references an `impl Trait` type in its return type
```

`async fn` in traits is built on the same mechanism, and has the same
restriction.

## Keeping a trait usable as dyn

If callers need trait objects, for a `Vec` of different implementations,
return a **boxed** iterator instead:

```rust
fn all(&self) -> Box<dyn Iterator<Item = String> + '_>;
```

Now every implementation returns the same type, a `Box<dyn Iterator>`, so
the vtable has one fixed entry, and `Vec<Box<dyn Repository>>` works. It
costs one allocation per call, and dynamic dispatch for each item. The
`+ '_` means "the iterator may borrow from `self`", the elided lifetime of
`&self`; without it, a boxed trait object would have to be `'static`
(Intermediate lesson 8) and could not iterate over `self`'s data.

The usual pattern in libraries is to offer both: a generic trait for
performance, and a dyn-compatible one for flexibility. A single method that
spoils dyn compatibility can also be fenced off with `where Self: Sized`,
keeping the rest of the trait usable as an object.

## Associated type bounds

Sometimes a function cares not only about what its argument *is*, but about
what it **yields**. "Any collection or iterator of things that can be viewed
as text" is written by bounding the associated type `Item`:

```rust
fn shout<I>(items: I) -> Vec<String>
where
    I: IntoIterator,
    I::Item: AsRef<str>,          // whatever it yields must be viewable as text
{
    items.into_iter().map(|s| s.as_ref().to_uppercase()).collect()
}
```

`I::Item` is the `Item` type of `I`'s `IntoIterator` implementation, and the
bound requires it to be `AsRef<str>`. So `shout(["a", "b"])` (an array of
`&str`), `shout(vec![String::from("c")])`, and a `Vec<Box<str>>` all work,
with no conversion at the call site. Since Rust 1.79 there is a shorthand that
puts the bound right inside: `fn f(x: impl Iterator<Item: Display>)`.

## Blanket impls and coherence, once more

`impl<T: Display> MyTrait for T {}` covers every displayable type at once
(Intermediate lesson 3), and the orphan rule still applies: either the trait
or the type must belong to your crate, so `impl Display for Vec<T>` is not
yours to write, and a newtype is the workaround. These rules, together
called **coherence**, guarantee that every type has at most one
implementation of each trait, which is what makes trait-based generic code
predictable.

## Run it

```rust
trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;
    fn next(&mut self) -> Option<Self::Item<'_>>;
}

/// Overlapping mutable windows of two - impossible with `Iterator`.
struct Windows {
    buf: Vec<i32>,
    pos: usize,
}

impl LendingIterator for Windows {
    type Item<'a> = &'a mut [i32];
    fn next(&mut self) -> Option<Self::Item<'_>> {
        if self.pos + 2 > self.buf.len() {
            return None;
        }
        let window = &mut self.buf[self.pos..self.pos + 2];
        self.pos += 1;
        Some(window)
    }
}

fn shout<I>(items: I) -> Vec<String>
where
    I: IntoIterator,
    I::Item: AsRef<str>,
{
    items.into_iter().map(|s| s.as_ref().to_uppercase()).collect()
}

fn main() {
    let mut w = Windows { buf: vec![1, 2, 3, 4], pos: 0 };
    while let Some(pair) = w.next() {
        pair[1] += pair[0];            // each window sees the last one's write
    }
    println!("{:?}", w.buf);
    println!("{:?} {:?}", shout(["a", "b"]), shout(vec![String::from("c")]));
}
```

```output
[1, 3, 6, 10]
["A", "B"] ["C"]
```

The windows overlap and are mutable: `[1, 2]` became `[1, 3]`, then the
window `[3, 3]` became `[3, 6]`, then `[6, 4]` became `[6, 10]`. Each saw
the previous one's write, giving running totals. Two such windows could
never exist at once, which is exactly what the lending signature lets the
compiler enforce. `w.buf` is readable after the loop because the last item's
borrow has ended.

## Your turn

In `src/lib.rs`:

- the `LendingIterator` trait with a GAT, as above, and
  `WindowsMut::new(slice, size)` implementing it, yielding overlapping
  **mutable** windows of `size` elements: windows of 2 over `[1, 2, 3, 4]`
  start at positions 0, 1 and 2, so adding 10 to each window's first element
  gives `[11, 12, 13, 4]`. Windows of 3 over 10 elements: 8 windows. A size
  of 0, or one larger than the slice, yields nothing. (The slice is borrowed
  for `'a`; reborrow `&mut self.data[start..end]` for each item.)
- the `Pipeline` trait with `fn steps(&self) -> impl Iterator<Item = &str>`
  and a **default** `describe()` joining the steps with `" -> "`
  (`"read -> transform -> write"`), implemented for `Simple`
- the dyn-compatible `Repository` trait, with `name(&self) -> &str`,
  `find(&self, id: usize) -> Option<String>` (the item at that position,
  as an owned `String`), and `all(&self) -> Box<dyn Iterator<Item = String>
  + '_>`; implement it for `MemoryRepo`
- `count_all(repos: &[Box<dyn Repository>]) -> usize`: the total number of
  items over all repositories, through `all()`
- `total_len(items)`: the total byte length of the items, accepting anything
  `IntoIterator` whose items are `AsRef<str>`: arrays of `&str`, `Vec<String>`,
  `Vec<Box<str>>`. The starter's signature has no bounds yet; add the `where`
  clause.
