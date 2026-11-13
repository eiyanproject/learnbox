---
title: Traits
summary: Shared behaviour across types, default methods, trait bounds, and dyn for mixed collections.
order: 10
files: [src/lib.rs]
run: cargo test
hints:
  - "Implement the trait per type: `impl Shape for Circle { fn area(&self) -> f64 { PI * self.radius * self.radius } fn name(&self) -> String { \"circle\".to_string() } }`."
  - "The default `describe` is written once in the trait body and can call `self.name()` and `self.area()`: `format!(\"{} with area {:.2}\", self.name(), self.area())`."
  - "`impl fmt::Display for Square { fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { write!(f, \"Square({})\", self.side) } }`."
  - "`total_area(shapes: &[Box<dyn Shape>])`: loop and add `shape.area()`. `largest<T: PartialOrd + Copy>`: keep the biggest seen so far, starting from `items[0]`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **trait** | a named set of abilities a type can have, such as "can report its area"; like an interface |
| **signature** (in a trait) | a method listed with no body, ending in `;`: implementers must provide it |
| **implement** | `impl Trait for Type`: say how a type has those abilities |
| **unit struct** | `struct Dog;`, a struct with no fields; its only value is `Dog` |
| **in scope** | a trait must be `use`d to call its methods from another module |
| **default method** | a trait method with a body; implementers get it free and may override it |
| **override** | write your own version of a default method |
| **bound** | `T: Speak`: "any type `T` that implements `Speak`" |
| **`impl Trait`** | the short form of a bound in a parameter: `thing: &impl Speak` |
| **`PartialOrd`** | the trait behind `<` and `>` |
| **combined bounds** | `T: PartialOrd + Copy` |
| **monomorphisation** | the compiler making a specialised copy of a generic function for each type used |
| **static dispatch** | which method to call is settled at compile time; as fast as non-generic code |
| **trait object** (`dyn Trait`) | "some value of a type that implements the trait", decided at run time |
| **`Box`** | a fixed-size pointer that owns a value on the heap |
| **dynamic dispatch** | the method is looked up while the program runs |
| **`Display`** | `{}` formatting and `.to_string()`; written by hand |
| **`Eq`**, **`Ord`**, **`Default`** | full equality; full ordering for sorting; a starting value |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `trait Speak { fn speak(&self) -> String; }` | declares a trait |
| `impl Speak for Dog { fn speak(&self) -> String { ... } }` | implements it |
| `fn shout(&self) -> String { self.speak().to_uppercase() + "!" }` | a default method |
| `fn announce<T: Speak>(thing: &T)`, `fn announce(thing: &impl Speak)` | generic with a bound, long and short |
| `fn largest<T: PartialOrd + Copy>(items: &[T]) -> T` | the generic largest |
| `Vec<Box<dyn Speak>>`, `Box::new(Dog)` | a mixed list of trait objects |
| `impl fmt::Display for Robot { fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { write!(f, "...") } }` | implements `Display` |
| `write!(f, "...")` | like `format!`, but writes into `f` |
| `{:.2}` | a number with 2 decimals |
| `shapes.iter().map(\|s\| s.area()).sum()` | adds up the areas |

### Errors

| Error | Means |
|---|---|
| `error[E0046]: not all trait items implemented, missing: speak` | an `impl` left out a required method |
| `error[E0277]: the trait bound Cat: Speak is not satisfied` | passed a type that does not implement the bound |
| `error[E0369]: binary operation > cannot be applied to type T` | a generic with no `PartialOrd` bound |
| `cannot move out of type [T], a non-copy slice` | copying out of a slice needs `Copy` |
| `mismatched types` in `vec![Dog, Robot {..}]` | one `Vec` holds one type; use `Box<dyn ...>` |

---

Say you have a `Circle`, a `Square` and a `Triangle`, and want one function
that prints the area of any of them. The function needs to know only one
thing about its argument: that it *has* an area. A **trait** names a set of
abilities like that ("can report its area", "can be printed", "can be
compared"), and each type says, separately, that it has them and how.
Traits are close to **interfaces** in Java, C# or Go.

You have used traits since lesson 4 without writing one: `Copy`, `Clone`,
`Debug` and `PartialEq` are all traits, and `#[derive]` implements them for
you. This lesson shows how to define your own and implement them by hand.

## Defining and implementing a trait

```rust
trait Speak {
    fn speak(&self) -> String;
}
```

(A fragment.) The trait lists method **signatures**, ending in `;` with no
body: anything that wants to be `Speak` must provide a `speak` method that
takes `&self` and returns a `String`. Implementing it for a type is an
`impl Trait for Type` block:

```rust
struct Dog;
struct Robot { id: u32 }

impl Speak for Dog {
    fn speak(&self) -> String {
        "woof".to_string()
    }
}

impl Speak for Robot {
    fn speak(&self) -> String {
        format!("unit {} online", self.id)
    }
}
```

(`struct Dog;` is a struct with no fields at all; its only value is written
`Dog`.) Each type decides for itself what speaking means. Leave a method out
and the compiler lists what is missing:

```rust
impl Speak for Dog {}
```

```text
error[E0046]: not all trait items implemented, missing: `speak`
 --> src/lib.rs:5:1
  |
2 |     fn speak(&self) -> String;
  |     -------------------------- `speak` from trait
...
5 | impl Speak for Dog {}
  | ^^^^^^^^^^^^^^^^^^ missing `speak` in implementation
```

The `...` stands for skipped source lines between the two that matter: line
2, where the trait asks for `speak`, and line 5, the `impl` that does not
give it.

One rule to know now: to call a trait's method, the trait must be in scope.
Within one file it always is; across modules you `use` it (the modules
lesson comes next, in the Intermediate track).

## Default methods

A trait can also give a method a body. Every implementer gets it for free,
and may still write its own version to **override** it:

```rust
trait Speak {
    fn speak(&self) -> String;

    fn shout(&self) -> String {
        self.speak().to_uppercase() + "!"
    }
}
```

`Dog.shout()` now works without `Dog` writing anything more: the default
calls `self.speak()`, which is `Dog`'s own `speak`, and turns `"woof"` into
`"WOOF!"`. This is a useful pattern: implementers write one small required
method, and the trait builds the rest on top of it. The standard `Iterator`
trait works that way: implement `next` and get `map`, `filter`, `sum` and
dozens more (lesson 11).

## Traits as bounds

A function can accept *any* type that implements a trait. The general form
uses a type parameter `T` with a **bound**, `T: Speak`, meaning "any type
`T`, as long as it implements `Speak`":

```rust
fn announce<T: Speak>(thing: &T) -> String {
    format!("It says: {}", thing.speak())
}
```

and the short form, for the common simple case, says the same:

```rust
fn announce(thing: &impl Speak) -> String {
    format!("It says: {}", thing.speak())
}
```

Inside `announce`, the bound is the *only* thing known about `thing`: you
may call `speak` (and `shout`) on it, and nothing else. In return, any
type that implements `Speak` can be passed. Pass one that does not, and the
error names both the type and the bound it fails:

```text
error[E0277]: the trait bound `Cat: Speak` is not satisfied
 --> src/lib.rs:4:33
  |
4 | pub fn f() -> String { announce(&Cat) }
  |                        -------- ^^^^ unsatisfied trait bound
  |                        |
  |                        required by a bound introduced by this call
  |
note: required by a bound in `announce`
```

Bounds also work the other way round. Here is a generic `largest` with no
bound at all:

```rust
fn largest<T>(items: &[T]) -> T {
    let mut big = items[0];
    for &x in items {
        if x > big { big = x; }
    }
    big
}
```

```text
error[E0369]: binary operation `>` cannot be applied to type `T`
  |
3 |         if x > big { big = x; }
  |            - ^ --- T
  |            |
  |            T
  |
help: consider restricting type parameter `T` with trait `PartialOrd`
  |
1 | fn largest<T: std::cmp::PartialOrd>(items: &[T]) -> T {
  |             ++++++++++++++++++++++
```

`T` could be any type at all, including ones that cannot be compared, so `>`
is not allowed. `PartialOrd` is the trait behind `<` and `>`. Add it, and the
next error is about `let mut big = items[0];`: copying a value out of the
slice needs `Copy` (lesson 4). Bounds combine with `+`, so the full signature
is `fn largest<T: PartialOrd + Copy>(items: &[T]) -> T`: "comparable, and
cheap to copy", exactly what this function needs. It then works for `i32`,
`f64`, `char` and any other such type.

The compiler turns a generic function into a separate, specialised copy for
each type it is used with (`largest::<i32>`, `largest::<char>`, ...). This is
called **static dispatch**: which `speak` to call is settled at compile time,
so a generic call is as fast as a call written for one type.

## dyn: mixing types in one collection

A `Vec<T>` holds values of one type, so `vec![Dog, Robot { id: 7 }]` does
not compile. To hold a `Dog` and a `Robot` together, store **trait
objects**:

```rust
let things: Vec<Box<dyn Speak>> = vec![Box::new(Dog), Box::new(Robot { id: 7 })];
for t in &things {
    println!("{}", t.speak());
}
```

Two new pieces:

- `dyn Speak` means "some value of a type that implements `Speak`; which
  type, we find out while the program runs". The type is not known at compile
  time, and neither is its size: a `Dog` takes 0 bytes, a `Robot` 4.
- A vector's slots must all be the same size, so the values cannot go in
  directly. `Box::new(value)` moves a value to the heap and gives back a
  `Box`, a fixed-size pointer that owns it. (Boxes get a full lesson in the
  Intermediate track.)

```text
 things (Vec on the heap)           each Box points at its own value
 [ Box ] ------------------------>  Dog
 [ Box ] ------------------------>  Robot { id: 7 }
```

Each `Box<dyn Speak>` also carries a pointer to the right type's `speak`, so
`t.speak()` looks up which function to call while the program runs. That is
**dynamic dispatch**: slightly slower than static dispatch, and the price of
mixing types.

When to use which: `impl Trait` / `<T: Trait>` when each call deals with one
type; `dyn Trait` when one collection or variable must hold different types.

## Standard traits you implement often

| Trait | Gives you | Usually |
|---|---|---|
| `Debug` | `{:?}` formatting | derived |
| `Display` | `{}` formatting, and `.to_string()` | written by hand |
| `Clone`, `Copy` | `.clone()`; copying instead of moving | derived |
| `PartialEq`, `Eq` | `==` and `!=` | derived |
| `PartialOrd`, `Ord` | `<`, `>`, sorting | derived |
| `Default` | `T::default()`, a starting value | derived |

`Display` cannot be derived, because only you know how your type should look
to a user. Implementing it looks like this:

```rust
use std::fmt;

impl fmt::Display for Robot {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Robot #{}", self.id)
    }
}
```

`fmt` is the one required method. `f` is where the text goes, and `write!`
works like `format!`, but writes into `f` and returns a `fmt::Result` saying
whether that worked, which `fmt` passes straight back. In return, `{}` works
for `Robot`, and so does `.to_string()`: the standard library implements
`to_string` for every type that implements `Display`.

## Run it

```rust
use std::fmt;

trait Speak {
    fn speak(&self) -> String;

    fn shout(&self) -> String {
        self.speak().to_uppercase() + "!"
    }
}

struct Dog;
struct Robot {
    id: u32,
}

impl Speak for Dog {
    fn speak(&self) -> String {
        "woof".to_string()
    }
}

impl Speak for Robot {
    fn speak(&self) -> String {
        format!("unit {} online", self.id)
    }
}

impl fmt::Display for Robot {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Robot #{}", self.id)
    }
}

fn announce(thing: &impl Speak) -> String {
    format!("It says: {}", thing.speak())
}

fn largest<T: PartialOrd + Copy>(items: &[T]) -> T {
    let mut big = items[0];
    for &x in items {
        if x > big {
            big = x;
        }
    }
    big
}

fn main() {
    println!("{}", Dog.shout());
    println!("{}", announce(&Robot { id: 7 }));
    let things: Vec<Box<dyn Speak>> = vec![Box::new(Dog), Box::new(Robot { id: 7 })];
    for t in &things {
        println!("{}", t.speak());
    }
    let r = Robot { id: 3 };
    println!("{r} / {}", r.to_string());    // Display gives to_string for free
    println!("{} {} {}", largest(&[3, 9, 2]), largest(&[1.5, -0.5]), largest(&['a', 'z']));
}
```

```output
WOOF!
It says: unit 7 online
woof
unit 7 online
Robot #3 / Robot #3
9 1.5 z
```

`Dog` never wrote `shout`; it got the default. The loop over `things` called
`Dog`'s `speak` for the first item and `Robot`'s for the second, chosen while
running. The same `largest` worked for integers, floats and characters.

## Your turn

In `src/lib.rs`:

- Implement `Shape` for `Circle` (area π × radius², name `"circle"`) and
  `Square` (area side², name `"square"`)
- Give the `Shape` trait a **default** method `describe()` returning
  `"<name> with area <area>"`, the area rounded to 2 decimals (`{:.2}`):
  `"square with area 4.00"`, `"circle with area 3.14"`. Write it once, in the
  trait, not in each `impl`.
- Implement `Display` for `Square`, printing `Square(<side>)`. The side is an
  `f64`, and `{}` prints `2.0` as `2` and `1.5` as `1.5`, which is exactly
  what is wanted: `Square(2)`, `Square(1.5)`.
- `total_area(shapes)`: the sum of all areas in a mixed list of boxed shapes;
  `0.0` for an empty list
- `largest(items)`: the largest item of a non-empty slice, for any type that
  is `PartialOrd + Copy`, as shown above
