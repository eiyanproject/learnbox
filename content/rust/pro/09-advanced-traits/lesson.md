---
title: Advanced traits
summary: Generic associated types, impl Trait in traits, associated type bounds, and keeping a trait usable as dyn.
order: 9
files: [src/lib.rs]
run: cargo test
hints:
  - "`LendingIterator` has `type Item<'a> where Self: 'a;` and `fn next(&mut self) -> Option<Self::Item<'_>>`. `WindowsMut` yields `&'a mut [i32]` by reborrowing `&mut self.data[start..end]`."
  - "`Pipeline::steps(&self) -> impl Iterator<Item = &str>` is return-position impl Trait in a trait (RPITIT); it makes the trait not dyn-compatible, so add a separate `dyn`-friendly trait for the object case."
  - "`total_len<I>(items: I) where I: IntoIterator, I::Item: AsRef<str>`: an associated type bound, so the function accepts iterators of `&str`, `String`, or anything else viewable as text."
  - "`Repository` stays dyn-compatible by returning `Box<dyn Iterator<Item = String> + '_>` instead of `impl Iterator`, so `Vec<Box<dyn Repository>>` still works."
---

## Generic associated types

An associated type can itself take generic parameters, most usefully a
lifetime. That is what makes a **lending iterator** possible: one that yields
items borrowing from itself, which `Iterator` cannot express.

```rust
pub trait LendingIterator {
    type Item<'a> where Self: 'a;
    fn next(&mut self) -> Option<Self::Item<'_>>;
}
```

`Iterator::Item` has no lifetime, so `next` cannot return something borrowed
from `&mut self` (two items could exist at once, aliasing the same data). With a
GAT, the borrow is tied to the call, and the compiler enforces that the previous
item is dropped before the next call. The price: the standard adapters
(`map`, `filter`, `collect`) are not available, because they are defined on `Iterator`.

## impl Trait in traits

A trait method can return `impl Trait`:

```rust
pub trait Pipeline {
    fn steps(&self) -> impl Iterator<Item = &str>;
}
```

This avoids boxing, but the trait is no longer **dyn-compatible**: each
implementation returns a different hidden type, so there is no single vtable
entry. `dyn Pipeline` will not compile.

## Keeping a trait usable as dyn

If callers need trait objects, return a boxed iterator instead:

```rust
fn names(&self) -> Box<dyn Iterator<Item = String> + '_>;
```

One allocation per call, and `Vec<Box<dyn Repository>>` works. The usual pattern
in libraries is both: a generic trait for performance, and an object-safe one
for flexibility. Methods that spoil dyn-compatibility can also be excluded with
`where Self: Sized`.

## Associated type bounds

Constrain an associated type inline, instead of a longer `where` clause:

```rust
fn shout<I>(items: I) -> Vec<String>
where
    I: IntoIterator,
    I::Item: AsRef<str>,          // whatever it yields must be viewable as text
{
    items.into_iter().map(|s| s.as_ref().to_uppercase()).collect()
}
```

`fn f(x: impl Iterator<Item: Display>)` is the shorthand form.

## Blanket impls and coherence

`impl<T: Display> MyTrait for T {}` covers every displayable type at once
(Intermediate: traits). Remember the orphan rule: either the trait or the type
must belong to your crate, so `impl Display for Vec<T>` is not yours to write.
The workaround is a newtype wrapper.

## Your turn

In `src/lib.rs`:

- `LendingIterator` with a GAT, and `WindowsMut::new(slice, size)` yielding
  overlapping **mutable** windows, so callers can modify the underlying data
- `Pipeline` with `fn steps(&self) -> impl Iterator<Item = &str>`, implemented
  for `Simple` (a `Vec<String>`)
- `Repository`: a dyn-compatible trait with `name`, `find(id) -> Option<String>`
  and `all(&self) -> Box<dyn Iterator<Item = String> + '_>`, implemented for
  `MemoryRepo`, plus `count_all(&[Box<dyn Repository>]) -> usize`
- `total_len<I>(items)` using an associated type bound, accepting iterators of
  anything `AsRef<str>`
