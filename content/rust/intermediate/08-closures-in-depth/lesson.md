---
title: Closures in depth
summary: Fn, FnMut and FnOnce, how captures work, move closures, storing closures in structs, and returning them.
order: 8
files: [src/lib.rs]
run: cargo test
hints:
  - "`EventBus` stores `handlers: HashMap<String, Vec<Box<dyn Fn(&str) -> String>>>`. `on` takes `impl Fn(&str) -> String + 'static` and pushes `Box::new(handler)`."
  - "`make_counter()` returns `impl FnMut() -> u32`: `let mut count = 0; move || { count += 1; count }`."
  - "`apply_twice<F: FnMut(i32) -> i32>(mut f: F, x: i32) -> i32 { let y = f(x); f(y) }`; the parameter must be `mut` because calling an `FnMut` changes it."
  - "`run_once<F: FnOnce() -> String>(f: F) -> String { f() }`. `compose` returns `impl Fn(i32) -> i32` with `move |x| g(f(x))`, requiring `F: Fn(i32) -> i32` and `G: Fn(i32) -> i32`."
---

Beginner lesson 11 introduced closures and the three traits `Fn`, `FnMut`
and `FnOnce`. This lesson goes underneath: what a closure *is* in memory,
why the three traits exist, how to choose the right one when you **accept**
a closure, and how to **store** closures in a struct, which is how callbacks,
event handlers and plug-in hooks are written in Rust.

## What a closure is

A closure is two things: the code in its body, and the values it captured.
The compiler turns each closure into an anonymous struct holding the
captures, plus an implementation of the call. This closure:

```rust
let threshold = 10;
let is_big = |x: i32| x > threshold;
```

is compiled into something like:

```rust
struct IsBigClosure<'a> {
    threshold: &'a i32,             // captured by reference: it only reads it
}

impl Fn(i32) -> bool for IsBigClosure<'_> {   // (not real syntax)
    fn call(&self, x: i32) -> bool { x > *self.threshold }
}
```

(A sketch, not code you can write.) Two consequences explain the rest of this
lesson:

- **Every closure has its own type**, unnamed and different from every other
  closure's, even one with the same signature. That is why you cannot write
  the type of a closure, and accept or return closures through traits
  instead.
- What a closure may do with its captures is decided by how it holds them,
  which is what the three traits describe.

## What a closure captures

A closure captures each outside variable in the least demanding way that its
body allows:

```rust
let name = String::from("Ana");
let greet = || println!("hi {name}");     // only reads name: borrows it (&)

let mut count = 0;
let mut inc = || count += 1;              // changes count: borrows it mutably (&mut)

let data = vec![1, 2, 3];
let consume = move || drop(data);         // takes ownership of data
```

(A fragment.) The ordinary borrow rules then apply to the closure as if it
were a reference: while `inc` exists and will be used again, nothing else
may touch `count`, because `inc` holds `&mut count`.

## The three traits

Which traits a closure implements depends on what its body does with its
captures:

| Trait | Called through | The body... | Can be called |
|---|---|---|---|
| `Fn` | `&self` | only reads its captures | any number of times, even several at once |
| `FnMut` | `&mut self` | changes a capture | many times, one at a time |
| `FnOnce` | `self` (consumes it) | moves a capture out | once |

They form a hierarchy: every `Fn` closure is also `FnMut`, and every `FnMut`
is also `FnOnce`. (Something you can call through `&self` can certainly be
called through `&mut self`, and something you may call many times you may
call once.)

That hierarchy tells you how to choose a bound when a function **accepts** a
closure: ask for the *least* you need, because a weaker requirement accepts
more closures.

| Your function calls it... | Bound | Accepts |
|---|---|---|
| exactly once | `FnOnce` | every closure |
| repeatedly, one call at a time | `FnMut` | everything except closures that move captures out |
| repeatedly, possibly while shared | `Fn` | only closures that just read |

Asking for too much rejects reasonable closures. This exercise's starter
asks `apply_twice` for `Fn`, and the tests pass it a closure that counts its
calls. Here is the same situation in one file:

```text
error[E0594]: cannot assign to `calls`, as it is a captured variable in a `Fn` closure
 --> src/lib.rs:4:23
  |
1 | pub fn apply_twice<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 { f(f(x)) }
  |                                          - change this to accept `FnMut` instead of `Fn`
...
4 |     apply_twice(|x| { calls += 1; x * 3 }, 2)
  |     ----------- ---   ^^^^^^^^^^ cannot assign
  |     |           |
  |     |           in this closure
  |     expects `Fn` instead of `FnMut`
```

Read the labels: the closure changes `calls`, `apply_twice` expects an `Fn`, and the
first label suggests the fix, in the function rather than in the closure.
`run_once` has the same problem with `FnOnce`: a closure that moves a
`String` out (`move || owned`) is rejected with
``error[E0507]: cannot move out of `owned`, a captured variable in an `Fn` closure``.

### Calling an FnMut

A function that accepts an `FnMut` needs its parameter to be `mut`, because
each call goes through `&mut self` and may change the closure's captured
state:

```rust
fn call_n<F: FnMut()>(mut f: F, n: usize) {
    for _ in 0..n {
        f();
    }
}
```

One more trap, which the exercise starter contains: `f(f(x))` calls `f`
while an outer call of `f` is being set up, which is two `&mut` borrows of
`f` at the same time:

```text
error[E0499]: cannot borrow `f` as mutable more than once at a time
  |
1 | pub fn apply_twice<F: FnMut(i32) -> i32>(mut f: F, x: i32) -> i32 { f(f(x)) }
  |                                                                     - ^ second mutable borrow occurs here
  |                                                                     |
  |                                                                     first mutable borrow occurs here
```

Split it into two statements, `let y = f(x); f(y)`, and each borrow ends
before the next begins. With `Fn`, `f(f(x))` was fine, since shared borrows
may overlap.

## move

`move` makes a closure take **ownership** of everything it captures, instead
of borrowing. You need it whenever the closure outlives the scope where its
captures live: when it is returned, stored in a struct that lives longer, or
sent to another thread (Advanced track). Beginner lesson 11 showed the E0373
error you get without it.

`move` changes **how** things are captured, not what the body does with
them, so it does not change the traits. A `move` closure that only reads its
captures is still `Fn`:

```rust
let prefix = String::from(">> ");
let tag = move |s: &str| format!("{prefix}{s}");   // owns prefix, only reads it: Fn
tag("a");
tag("b");                                         // fine: callable many times
```

(A fragment.) For `Copy` values such as an `i32`, `move` copies them into the
closure, and the original stays usable.

## Returning closures

Because every closure has its own unnamed type, a function cannot write the
return type out. `impl Fn(...)` says "some type implementing this trait,
which I am not naming":

```rust
fn adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}
```

A closure that keeps state between calls is returned as `impl FnMut`. Its
captured variable lives inside the closure, so each closure made this way has
its **own** copy, the basis of the exercise's `make_counter`:

```rust
fn make_counter() -> impl FnMut() -> u32 {
    let mut count = 0;
    move || {
        count += 1;
        count
    }
}
```

(A fragment.) `count` is moved into the closure, where it lives on after
`make_counter` returns. Every call of `make_counter` makes a new closure
with a new `count`, starting at 0. The caller must store it with `let mut`,
since calling an `FnMut` changes it.

`impl Trait` in return position names exactly one type, so a function cannot
return one closure in one branch and a different one in another; for that,
return `Box<dyn Fn(i32) -> i32>`.

## Storing closures

A struct that holds **one** kind of closure can be generic over it:

```rust
struct Retry<F: Fn() -> bool> {
    attempt: F,
    times: u32,
}
```

(A fragment.) That avoids any boxing: the closure is stored directly, and
calls to it are static (lesson 3).

A struct or collection that holds **different** closures cannot do that,
since `F` is a single type and each closure has its own. It needs trait
objects, one box per closure (Beginner lesson 10):

```rust
struct Button {
    on_click: Vec<Box<dyn Fn() -> String>>,
}
```

There is one more requirement. A `Box<dyn Fn() -> String>` stored in a
struct, without a lifetime written, means `Box<dyn Fn() -> String + 'static>`:
the closure must not hold references to anything that might be dropped
before it is. A closure that captures **only owned data**, which a `move`
closure over `String`s or numbers does, satisfies `'static`. A method that
accepts any `impl Fn` and boxes it must therefore say so:

```rust
pub fn on(&mut self, handler: impl Fn(&str) -> String) {
    self.handlers.push(Box::new(handler));
}
```

```text
error[E0310]: the parameter type `impl Fn(&str) -> String` may not live long enough
  |
4 |         self.handlers.push(Box::new(handler));
  |                            ^^^^^^^^^^^^^^^^^
  |                            |
  |                            the parameter type `impl Fn(&str) -> String` must be valid for the static lifetime...
  |
help: consider adding an explicit lifetime bound
  |
3 |     pub fn on(&mut self, handler: impl Fn(&str) -> String + 'static) {
  |                                                           +++++++++
```

The `help:` is the fix: `+ 'static` on the parameter. Callers can then pass
closures over owned data, and the compiler rejects ones that borrow local
variables, which would dangle once the function that created them returned.

## Run it

```rust
fn call_n<F: FnMut()>(mut f: F, n: usize) {
    for _ in 0..n {
        f();
    }
}

fn adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

fn run_once<F: FnOnce() -> Vec<i32>>(f: F) -> Vec<i32> {
    f()
}

struct Button {
    on_click: Vec<Box<dyn Fn() -> String>>,
}

fn main() {
    let name = String::from("Ana");
    let greet = || format!("hi {name}");      // Fn: only reads
    println!("{} {}", greet(), name);         // name was only borrowed

    let mut count = 0;
    call_n(|| count += 1, 3);                 // FnMut: changes a capture
    println!("{count}");

    let data = vec![1, 2, 3];
    let give_back = move || data;             // FnOnce: moves data out
    println!("{:?}", run_once(give_back));

    println!("{}", adder(10)(5));

    let label = String::from("ok");
    let button = Button {
        on_click: vec![Box::new(|| "clicked".to_string()), Box::new(move || label.clone())],
    };
    let results: Vec<String> = button.on_click.iter().map(|f| f()).collect();
    println!("{results:?}");
}
```

```output
hi Ana Ana
3
[1, 2, 3]
15
["clicked", "ok"]
```

`give_back` returns `data` itself, moving it out of the closure, so it is
`FnOnce` and only `run_once` could accept it. In the `Button`, the second
handler owns `label` (`move`) and returns a clone each time, because handing
out `label` itself would move it and make the closure `FnOnce`. That is a
common shape for stored callbacks: own the data, clone on each call.

## Your turn

In `src/lib.rs`:

- `EventBus`, a registry of handlers per event name:
  - `new()`, with no handlers
  - `on(&mut self, event: &str, handler)`: registers a `Fn(&str) -> String`
    handler for `event`; several handlers per event are allowed. The tests
    register a `move` closure that owns a `String`, so the parameter needs
    `+ 'static`, as above.
  - `emit(&self, event: &str, payload: &str) -> Vec<String>`: calls every
    handler for `event` with `payload`, in the order they were registered,
    and returns their results; an empty `Vec` for an event with no handlers
  - `handler_count(&self, event: &str) -> usize`, 0 for unknown events
- `make_counter()`: returns a closure that returns 1, 2, 3, ... on
  successive calls; two counters count independently
- `apply_twice(f, x)`: `f(f(x))`, but accepting `FnMut` closures. Change the
  bound, make the parameter `mut`, and split the nested call, as described
  above.
- `run_once(f)`: change the bound to `FnOnce`, so a closure that moves a
  `String` out is accepted
- `compose(f, g)`: returns a closure computing `g(f(x))`: `f` first, then `g`.
  `compose(|x| x + 1, |x| x * 2)` applied to 3 is 8.
