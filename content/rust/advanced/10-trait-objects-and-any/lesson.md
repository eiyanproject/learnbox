---
title: Trait objects and dynamic dispatch
summary: How dyn Trait works, object safety, heterogeneous collections, downcasting with Any, and choosing between generics and trait objects.
order: 10
files: [src/lib.rs]
run: cargo test
hints:
  - "`Plugin` is object safe: `fn name(&self) -> &str; fn run(&mut self, input: &str) -> String; fn as_any(&self) -> &dyn Any;`. Each implementation's `as_any` is `self`."
  - "`Registry` holds `Vec<Box<dyn Plugin>>`; `run_all(&mut self, input)` threads the output of one plugin into the next with a loop over `self.plugins.iter_mut()`."
  - "`find::<T: Plugin + 'static>(&self) -> Option<&T>`: `self.plugins.iter().find_map(|p| p.as_any().downcast_ref::<T>())`."
  - "`describe_value(value: &dyn Any)`: try `value.downcast_ref::<i32>()`, then `String`, then `&str`, and fall back to `\"something else\"`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **trait object** | `dyn Trait`: some value of a type implementing the trait, chosen at run time |
| **dispatch** | picking which implementation of a method to run |
| **static dispatch** | the method is chosen at compile time, per type |
| **monomorphisation** | the compiler making one copy of a generic function per concrete type |
| **inlining** | copying a method's body into the caller |
| **dynamic dispatch** | the method is looked up while running |
| **fat pointer** | a reference to a trait object: a data pointer and a vtable pointer |
| **vtable** | a per-type table of method addresses |
| **unsized** | `dyn Widget` has no size known at compile time, so it lives behind a pointer |
| **dyn compatibility** (object safety) | whether a trait can be used as `dyn`: methods take `self` by pointer, do not return `Self`, have no type parameters |
| **`where Self: Sized`** | fences off a method so the rest of the trait stays dyn compatible |
| **plugin** | code the main program runs without knowing its type in advance |
| **`Any`** | a trait every `'static` type has, allowing checked downcasting |
| **`TypeId`** | a unique id per type |
| **downcast** | get the concrete type back: `Some(&T)` if it matches exactly |
| **`as_any`** | the usual method that turns `&self` into `&dyn Any` |
| **trait upcasting** | since Rust 1.86, `&dyn Widget` converting to `&dyn Any` when `Any` is a supertrait |
| **escape hatch** | a way around the normal rules, to use rarely; often an enum is better |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests, which add a plugin of their own |

### Rust names

| Name | What it does |
|---|---|
| `fn draw(w: &impl Widget)` vs `fn draw(w: &dyn Widget)` | static vs dynamic dispatch |
| `Box<dyn Plugin>`, `Rc<dyn T>`, `Arc<dyn T + Send + Sync>` | pointers that can hold trait objects |
| `use std::any::Any;` | brings in `Any` |
| `fn as_any(&self) -> &dyn Any { self }` | the downcasting helper |
| `value.downcast_ref::<i32>()` | `Some(&i32)` or `None` |
| `fn find<T: Plugin + 'static>(&self) -> Option<&T>` | a typed lookup in the registry |
| `self.plugins.iter().find_map(\|p\| p.as_any().downcast_ref::<T>())` | the first plugin of type `T` |
| `self.plugins.iter_mut()` | each plugin mutably, for `run` |
| `std::mem::size_of::<&dyn Widget>()` | 16: two pointers |

### Errors

| Error | Means |
|---|---|
| `error[E0038]: the trait Shape is not dyn compatible` | a method returns `Self` or is generic |
| `for a trait to be dyn compatible it needs to allow building a vtable` | the compiler's note on why |
| `the size for values of type dyn Widget cannot be known` | a trait object used without a pointer |

---

`Box<dyn Trait>` has come up several times: for a list of different shapes
(Beginner lesson 10), for errors of any type (Intermediate lesson 2), for
stored callbacks (Intermediate lesson 8). This lesson looks at how trait
objects actually work, which explains their rules: why some traits cannot be
used as `dyn`, why a `&dyn Trait` is twice the size of a normal reference,
and how, when you really must, you can get the concrete type back out. The
exercise is a small plugin system, the classic use of trait objects: code
that runs plugins it has never seen, including ones written by its users.

## Static vs dynamic dispatch

Calling a trait method means picking which implementation to run, called
**dispatch**. Rust can do it at two different times.

With **generics**, the compiler makes a separate copy of the function for
each concrete type it is used with (**monomorphisation**, "making one form
each"). Each call goes straight to the right method, and can even be
**inlined**, the method's body copied into the caller:

```rust
fn render_all<T: Widget>(items: &[T]) { ... }     // every item is the same T
```

With a **trait object**, there is one copy of the function, which works with
any implementing type chosen while the program runs:

```rust
fn render_all(items: &[Box<dyn Widget>]) { ... }  // items may be different types
```

(Signatures.) How does that one copy know which `render` to call? A
reference to a trait object is a **fat pointer**, two pointers side by side:
one to the value's data, and one to a **vtable** (virtual method table), a
small table the compiler builds for each type that implements the trait,
holding the addresses of that type's methods:

```text
 &dyn Widget ─┬─ data   ─────> Button { label: "OK" }
              └─ vtable ─────> Button's vtable: [ drop, size, align, name, as_any ]

 &dyn Widget ─┬─ data   ─────> Slider
              └─ vtable ─────> Slider's vtable: [ drop, size, align, name, as_any ]
```

A call such as `w.name()` reads the address from the vtable and jumps
there. That costs one extra lookup, and prevents inlining, but lets
different types share one function and one `Vec`.

`dyn Widget` itself has no size known at compile time (a `Button` and a
`Slider` differ), so it always lives behind some pointer: `&dyn Widget`,
`&mut dyn Widget`, `Box<dyn Widget>`, `Rc<dyn Widget>`, or
`Arc<dyn Widget + Send + Sync>` to share one across threads.

Which to choose:

| Prefer generics when | Prefer trait objects when |
|---|---|
| the type is known at compile time | the set of types is open or chosen at run time (plugins) |
| speed matters in a hot loop | one collection must hold different types |
| | you want less generated code and faster compiles |

## Object safety (dyn compatibility)

Not every trait can be used as `dyn Trait`. A vtable needs one fixed entry
per method, callable without knowing the concrete type, and some methods
cannot provide that. Try a trait with a method that returns `Self`:

```rust
pub trait Shape {
    fn area(&self) -> f64;
    fn duplicate(&self) -> Self;
}

pub fn total(shapes: &[Box<dyn Shape>]) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}
```

```text
error[E0038]: the trait `Shape` is not dyn compatible
 --> src/lib.rs:6:28
  |
6 | pub fn total(shapes: &[Box<dyn Shape>]) -> f64 {
  |                            ^^^^^^^^^ `Shape` is not dyn compatible
  |
note: for a trait to be dyn compatible it needs to allow building a vtable
 --> src/lib.rs:3:28
  |
1 | pub trait Shape {
  |           ----- this trait is not dyn compatible...
2 |     fn area(&self) -> f64;
3 |     fn duplicate(&self) -> Self;
  |                            ^^^^ ...because method `duplicate` references the `Self` type in its return type
```

Called through a `&dyn Shape`, `duplicate` would return a value whose type,
and so whose size, is unknown, and the caller could not reserve space for
it. The compiler's current name for the property is **dyn compatibility**;
older material calls it **object safety**. Roughly, a trait is dyn compatible
when every method:

- takes `self` through a pointer: `&self`, `&mut self`, `self: Box<Self>`;
- does not return `Self` by value or otherwise use `Self` as a plain type;
- has no type parameters of its own (`fn map<T>(&self, ...)`), since a
  vtable cannot hold an entry for every possible `T`.

A method that breaks the rules can be fenced off with `where Self: Sized`,
which means "only callable on concrete types". The rest of the trait then
stays usable as an object. `Clone` is the famous non-dyn-compatible trait,
because `clone` returns `Self`.

## Any: recovering the concrete type

A `&dyn Plugin` only offers the trait's methods. Occasionally you need to get
back to the real type, for example to read a field that one specific plugin
has. `std::any::Any` allows checked **downcasting**:

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

(A fragment.) Every `'static` type (one containing no short-lived borrows)
implements `Any` automatically. Each type gets a unique `TypeId`, and
`downcast_ref::<T>()` compares the value's `TypeId` with `T`'s: if they
match, you get `Some(&T)`, otherwise `None`. The check is exact: a
`&dyn Any` holding a `String` is not a `&str`, and `downcast_ref::<&str>()`
on it is `None`. That is why the exercise's `describe_value` tries `String`
and `&str` separately. `downcast_mut` is the `&mut` version.

To downcast a `&dyn Plugin`, you first need it as a `&dyn Any`. The usual
pattern is an `as_any` method on the trait, which every implementation fills
in the same way:

```rust
trait Widget {
    fn name(&self) -> String;
    fn as_any(&self) -> &dyn Any;
}

impl Widget for Button {
    fn name(&self) -> String { "button".into() }
    fn as_any(&self) -> &dyn Any { self }     // a &Button coerces to &dyn Any
}
```

(A fragment.) Inside the `impl`, the compiler knows `self` is a `&Button`,
so it can build the `&dyn Any` with `Button`'s type information. Then
`widget.as_any().downcast_ref::<Button>()` works on any `&dyn Widget`.
(Since Rust 1.86 there is also **trait upcasting**: if `Widget` declares `Any`
as a supertrait, `trait Widget: Any`, a `&dyn Widget` converts to `&dyn Any`
directly. The `as_any` method is still common, and this exercise uses it:
the tests define a plugin of their own with an `as_any` method.)

Downcasting is an escape hatch. If you find yourself doing it a lot, the set
of types is probably closed and known, and an **enum** is the better model:
`match` is exhaustive and needs no run-time type checks.

## Run it

```rust
use std::any::Any;

fn describe(value: &dyn Any) -> String {
    if let Some(n) = value.downcast_ref::<i32>() {
        format!("an i32: {n}")
    } else {
        "something else".into()
    }
}

trait Widget {
    fn name(&self) -> String;
    fn as_any(&self) -> &dyn Any;
}

struct Button {
    label: String,
}
struct Slider;

impl Widget for Button {
    fn name(&self) -> String {
        "button".into()
    }
    fn as_any(&self) -> &dyn Any {
        self
    }
}

impl Widget for Slider {
    fn name(&self) -> String {
        "slider".into()
    }
    fn as_any(&self) -> &dyn Any {
        self
    }
}

fn main() {
    println!("{} | {}", describe(&7_i32), describe(&"seven"));
    let items: Vec<Box<dyn Widget>> = vec![Box::new(Button { label: "OK".into() }), Box::new(Slider)];
    for w in &items {
        match w.as_any().downcast_ref::<Button>() {
            Some(b) => println!("{} with label {}", w.name(), b.label),
            None => println!("{}", w.name()),
        }
    }
    println!("{} {}", std::mem::size_of::<&dyn Widget>(), std::mem::size_of::<&Button>());
}
```

```output
an i32: 7 | something else
button with label OK
slider
16 8
```

`describe(&"seven")` got a `&&str`, not an `i32`, so the downcast failed.
The loop called each item's own `name` through its vtable, and only the
`Button` downcast succeeded, giving access to its `label`, which `Widget`
knows nothing about. The last line shows the fat pointer: a `&dyn Widget` is
two pointers wide (16 bytes on a 64-bit machine), the data and the vtable,
where a plain reference is one.

## Your turn

In `src/lib.rs`:

- trait `Plugin`, dyn compatible, with three methods (the tests implement
  it for a plugin of their own with exactly these signatures):
  - `fn name(&self) -> &str`
  - `fn run(&mut self, input: &str) -> String`
  - `fn as_any(&self) -> &dyn Any`
- three plugins:
  - `Uppercase`, named `"upper"`: returns the input upper-cased
  - `Counter`, named `"counter"`: returns the input unchanged, and adds 1 to
    its public `calls` field on each run (which is why `run` takes
    `&mut self`)
  - `Suffix(String)`, named `"suffix"`: returns the input with its string
    added at the end
- `Registry`:
  - `register(&mut self, plugin: Box<dyn Plugin>)`
  - `names(&self) -> Vec<&str>` (or `Vec<String>`), in registration order
  - `run_all(&mut self, input: &str) -> String`: runs every plugin in order,
    each one getting the previous one's output; with no plugins, the input
    comes back unchanged. Counter, then Uppercase, then Suffix("!") turn
    `"hello"` into `"HELLO!"`.
  - `find::<T>(&self) -> Option<&T>`: the first registered plugin whose
    concrete type is `T`, through `as_any` and `downcast_ref`; `None` if
    there is none. `T` needs the bounds `Plugin + 'static`.
- `describe_value(&dyn Any) -> String`: `"i32 42"` for an `i32`,
  `"String hello"` for a `String`, `"&str hi"` for a `&str`, and
  `"something else"` for anything else
