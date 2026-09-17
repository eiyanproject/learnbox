---
title: Trait objects and dynamic dispatch
summary: How dyn Trait works, object safety, heterogeneous collections, downcasting with Any, and choosing between generics and trait objects.
order: 10
files: [src/lib.rs]
run: cargo test
hints:
  - "`Plugin` is object safe: `fn name(&self) -> &str; fn run(&mut self, input: &str) -> String; fn as_any(&self) -> &dyn Any;`. Each implementation's `as_any` is just `self`."
  - "`Registry` holds `Vec<Box<dyn Plugin>>`; `run_all(&mut self, input)` threads the output of one plugin into the next with a loop over `self.plugins.iter_mut()`."
  - "`find::<T: Plugin + 'static>(&self) -> Option<&T>`: `self.plugins.iter().find_map(|p| p.as_any().downcast_ref::<T>())`."
  - "`describe_value(value: &dyn Any)`: try `value.downcast_ref::<i32>()`, then `String`, then `&str`, and fall back to `\"something else\"`."
---

## Static vs dynamic dispatch

With generics, the compiler generates a copy of the function for each concrete
type (**monomorphisation**): calls are direct and can be inlined.

```rust
fn render_all<T: Widget>(items: &[T]) { ... }     // every item is the same T
```

With a **trait object**, one function works on any implementor chosen at
runtime, through a pointer to a vtable of methods:

```rust
fn render_all(items: &[Box<dyn Widget>]) { ... }  // items can be different types
```

`dyn Widget` has no known size, so it always lives behind a pointer:
`&dyn Widget`, `Box<dyn Widget>`, `Rc<dyn Widget>`, `Arc<dyn Widget + Send + Sync>`.

Choose generics for speed and when the type is known at compile time; trait
objects for plugins, heterogeneous collections, and to keep binary size and
compile times down.

## Object safety

Not every trait can become `dyn Trait`. Roughly, every method must be callable
without knowing the concrete type:

- no generic methods (`fn map<T>(&self, ...)`)
- no returning `Self` by value (`fn clone(&self) -> Self`)
- the receiver is `&self`, `&mut self`, `Box<Self>` and so on

Methods that break the rules can be excluded with `where Self: Sized`, which
keeps the rest of the trait usable as an object.

## Any: recovering the concrete type

Occasionally you need to get back from `&dyn Trait` to the real type, for
example to call a method one plugin has that the trait does not. `std::any::Any`
allows checked downcasting for `'static` types:

```rust
use std::any::Any;

fn describe(value: &dyn Any) -> String {
    if let Some(n) = value.downcast_ref::<i32>() {
        format!("an i32: {n}")
    } else {
        "something else".into()
    }
}
```

A trait object cannot be turned into `&dyn Any` directly, so the usual pattern
is an `as_any` method on the trait that each implementor fills in with `self`.

Downcasting is an escape hatch. If you find yourself doing it a lot, an enum is
often the better model: the set of variants is closed and `match` is exhaustive.

## Your turn

In `src/lib.rs`:

- trait `Plugin`: `name`, `run(&mut self, input) -> String`, `as_any`
- `Uppercase` (name `"upper"`), `Counter` (name `"counter"`, returns the input
  unchanged but counts calls in a public `calls` field), `Suffix(String)`
  (name `"suffix"`, appends its string)
- `Registry`: `register(Box<dyn Plugin>)`, `names()`, `run_all(input)` feeding
  each plugin's output to the next, and `find::<T>()` returning the first plugin
  of concrete type `T`
- `describe_value(&dyn Any)`: `"i32 42"`, `"String hello"`, `"&str hi"`, or
  `"something else"`
