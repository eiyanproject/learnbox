---
title: Threads
summary: Spawn and join OS threads, move data into them, borrow safely with scoped threads, and see how Send and Sync make data races a compile error.
order: 1
files: [src/lib.rs]
run: cargo test
hints:
  - "`parallel_sum`: `nums.chunks(chunk_size)` inside `thread::scope(|s| { ... })`; spawn one scoped thread per chunk with `s.spawn(move || chunk.iter().sum::<i64>())`, then join them all and add the results."
  - "`chunk_size` should be `nums.len().div_ceil(threads).max(1)` so there are at most `threads` chunks and never a zero-sized chunk."
  - "`spawn_workers(n)`: `(0..n).map(|i| thread::spawn(move || format!(\"worker {i} done\"))).collect::<Vec<_>>()`, then `into_iter().map(|h| h.join().unwrap())`."
  - "`count_matches`: scoped threads can borrow `words` and `needle` without `Arc`: `s.spawn(|| chunk.iter().filter(|w| **w == needle).count())`."
---

So far every program did one thing at a time. A modern computer has several
**cores**, each able to run code at the same time as the others. A
**thread** is an independent sequence of instructions within one program;
with several threads, a program can use several cores at once, finishing
CPU-heavy work sooner, or keep responding while it waits for something slow.

Threads have a famous danger: the **data race**. Two threads touch the same
memory at the same time, at least one of them writing, without anything to
order them. The result depends on exact timing, so the bug shows up
rarely, differently each time, and vanishes under a debugger. In most
languages, avoiding races is the programmer's job. In Rust, the ownership
and borrowing rules you already know extend to threads, and a program with a
data race **does not compile**. This lesson shows how.

## Spawning and joining

`std::thread::spawn` starts a new thread running a closure, and returns a
**join handle** for it:

```rust
use std::thread;

let handle = thread::spawn(|| {
    (1..=10).sum::<u64>()
});
let total = handle.join().unwrap();     // wait for it, and get the closure's return value
```

(A fragment.) From the moment `spawn` returns, the new thread and the
current one run at the same time, in no fixed order. `handle.join()` waits
until that thread has finished, and gives back what its closure returned.
Threads that are never joined are cut off when `main` returns, so join the
ones whose work matters.

`join` returns a `Result`: `Ok(value)` normally, and `Err` if the thread
**panicked**. A panic ends only the thread it happens in; the rest of the
program carries on, and `join` hands the failure back so a crashed worker
cannot silently vanish. (`.unwrap()` here means "if the worker panicked,
panic here too".)

## move: a thread must own what it uses

A spawned thread might keep running after the function that started it has
returned. So its closure cannot borrow that function's local variables;
they could be dropped while the thread still uses them:

```rust
let name = String::from("worker");
let h = thread::spawn(|| println!("{name}"));
```

```text
error[E0373]: closure may outlive the current function, but it borrows `name`, which is owned by the current function
 --> src/main.rs:4:27
  |
4 |     let h = thread::spawn(|| println!("{name}"));
  |                           ^^            ---- `name` is borrowed here
  |                           |
  |                           may outlive borrowed value `name`
  |
note: function requires argument type to outlive `'static`
help: to force the closure to take ownership of `name` (and any other referenced variables), use the `move` keyword
  |
4 |     let h = thread::spawn(move || println!("{name}"));
  |                           ++++
```

The `note:` names the rule behind it: `spawn` requires its closure to be
`'static` (Intermediate lesson 10), "holds no borrows that could expire".
`move` makes the closure own `name`, which satisfies that. After the move,
`name` belongs to the new thread, and the original function can no longer
use it, so the two threads can never touch it at the same time.

## Scoped threads: borrowing is fine again

Often you want threads only for a while: split some work, run the parts in
parallel, wait for all of them, carry on. For that, the "might outlive the
function" problem does not exist, and `thread::scope` lets the compiler see
it:

```rust
let data = vec![1, 2, 3, 4];
let (left, right) = data.split_at(2);

let total = thread::scope(|s| {
    let a = s.spawn(|| left.iter().sum::<i32>());
    let b = s.spawn(|| right.iter().sum::<i32>());
    a.join().unwrap() + b.join().unwrap()
});
```

(A fragment.) `thread::scope` runs its closure with a **scope** `s`, and
threads started with `s.spawn` belong to it. The promise is: `thread::scope`
does not return until every thread spawned in it has finished (it joins any
you did not join yourself). Since the threads cannot outlive the scope, and
the scope cannot outlive `data`, the threads may **borrow** `data`, `left` and
`right`. There is no `move`, no `Arc`, and no cloning, and `data` is still
usable afterwards.

```text
 main:    data ──────────────────────────────────────────────── still usable
          thread::scope( ────────────────────────────── ) returns here
            thread a:  sums left ───┤
            thread b:  sums right ──────┤
                                        all joined before scope returns
```

For "split this work across cores and wait", scoped threads are usually the
right tool. `thread::spawn` is for threads that live independently, such as
a background worker.

## Send and Sync: how the compiler knows

The borrow rules handle *references* across threads. Some types are unsafe
to use from two threads for other reasons: `Rc` (Intermediate lesson 5)
updates its counter with an ordinary `+= 1`, and two threads cloning the
same `Rc` at once could each read 3 and both write 4, losing a count and
freeing the value too early. The compiler tracks this with two **marker
traits**, traits with no methods that only say something about a type:

- `Send`: a value of this type can be **moved** to another thread.
- `Sync`: a value of this type can be **shared** between threads by
  reference. (Precisely: `T` is `Sync` if `&T` is `Send`.)

You never implement these by hand for normal code. The compiler implements
them automatically for every type whose fields are all `Send` (or all
`Sync`), and `thread::spawn` requires its closure, and so everything it
captures, to be `Send`. Most types are both: numbers, `String`, `Vec<T>` of
`Send` items, your own structs of those. The exceptions are the types built
for single-threaded use:

| Type | `Send` | `Sync` | Why |
|---|---|---|---|
| `Rc<T>` | no | no | its counter is not updated atomically |
| `RefCell<T>` | yes | no | its borrow counting is not thread-safe; one owner may move it, but not share it |
| `Arc<T>`, `Mutex<T>` | yes | yes | built for threads (lessons 2 and 3) |

Moving an `Rc` into a thread is therefore a compile error, not a crash
months later:

```text
error[E0277]: `Rc<i32>` cannot be sent between threads safely
 --> src/main.rs:5:27
  |
5 |     let h = thread::spawn(move || println!("{shared}"));
  |             ------------- -------^^^^^^^^^^^^^^^^^^^^^
  |             |             |
  |             |             `Rc<i32>` cannot be sent between threads safely
  |             required by a bound introduced by this call
  |
  = help: within `{closure@src/main.rs:5:27: 5:34}`, the trait `Send` is not implemented for `Rc<i32>`
```

The next two lessons give the thread-safe tools: channels for passing values
between threads, and `Arc` with `Mutex` for sharing them.

## How many threads?

`thread::available_parallelism()` reports how many threads the machine can
really run at once, usually the number of cores. For CPU-bound work,
spawning far more threads than that only adds the cost of switching between
them. In this course's container, a learner's processes also share a limit
on the number of processes and threads, so spawning thousands would fail.

Dividing work among threads usually means splitting a slice into **chunks**.
`slice.chunks(size)` gives consecutive sub-slices of `size` items, the last
one possibly shorter: `[1, 2, 3, 4, 5].chunks(2)` gives `[1, 2]`, `[3, 4]`,
`[5]`. To get at most `t` chunks out of `len` items, the size is `len / t`
rounded **up**: `len.div_ceil(t)`. And `chunks(0)` panics, so an empty slice
needs a size of at least 1, which `.max(1)` guarantees.

## Run it

```rust
use std::thread;

fn main() {
    let handle = thread::spawn(|| (1..=10).sum::<u64>());
    println!("{}", handle.join().unwrap());

    let name = String::from("worker");
    let h = thread::spawn(move || format!("{name} done"));
    println!("{}", h.join().unwrap());

    let data = vec![1, 2, 3, 4];
    let (left, right) = data.split_at(2);
    let total = thread::scope(|s| {
        let a = s.spawn(|| left.iter().sum::<i32>());
        let b = s.spawn(|| right.iter().sum::<i32>());
        a.join().unwrap() + b.join().unwrap()
    });
    println!("{total} {}", data.len());       // data is still ours

    let sizes: Vec<usize> = [1, 2, 3, 4, 5].chunks(5usize.div_ceil(2)).map(|c| c.len()).collect();
    println!("{sizes:?}");

    let crashed = thread::spawn(|| -> i32 { panic!("boom") }).join();
    println!("{}", crashed.is_err());
}
```

```output
55
worker done
10 4
[3, 2]
true
```

Five items in at most two chunks gave sizes 3 and 2. The last line's panic
does not appear above because its message goes to **standard error**, not
standard output:

```text
thread '<unnamed>' (4242) panicked at src/main.rs:23:45:
boom
```

Spawned threads have no name unless you give them one, hence
`'<unnamed>'`. The program carried on, because `join` handed the panic back
as an `Err`.

## Your turn

In `src/lib.rs`:

- `parallel_sum(nums, threads)`: split `nums` into **at most** `threads`
  chunks, sum each chunk in its own scoped thread, and add the results. It
  must also work when there are more threads than numbers (`&[1, 2, 3]`
  with 8 threads is 6) and for an empty slice (0).
- `spawn_workers(n)`: spawn `n` threads with `thread::spawn`, thread `i`
  returning `"worker <i> done"`; join them all, and return the messages in
  order of `i`, whatever order the threads happened to finish in. Spawn all
  of them first, then join; spawning and joining one at a time would run
  them one after another.
- `count_matches(words, needle, threads)`: how many items of `words` equal
  `needle` exactly, counted in scoped threads that **borrow** `words` and
  `needle`, again at most `threads` chunks
- `panicking_worker_is_reported()`: spawn a thread that panics, and return
  `true` if `join` reported the panic (as an `Err`). The test silences the
  panic message for you.

The tests also read your source and check it contains `thread::scope`.
