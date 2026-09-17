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

Rust threads are real OS threads. What makes them different from most
languages is that the compiler rules out **data races** before the program
runs.

## Spawning and joining

```rust
use std::thread;

let handle = thread::spawn(|| {
    (1..=10).sum::<u64>()
});
let total = handle.join().unwrap();     // wait, and get the closure's return value
```

`join` returns `Err` if the thread panicked, so a crashing worker does not
silently vanish.

## move: threads must own what they use

A spawned thread might outlive the function that started it, so its closure
cannot borrow local variables:

```rust
let name = String::from("worker");
thread::spawn(|| println!("{name}"));        // error: may outlive borrowed value
thread::spawn(move || println!("{name}"));   // ok: the thread owns name
```

This is the `'static` bound on `thread::spawn` in action.

## Scoped threads: borrowing is fine again

`thread::scope` guarantees every thread it spawns is joined before the scope
ends, so those threads **can** borrow local data:

```rust
let data = vec![1, 2, 3, 4];
let (left, right) = data.split_at(2);

let total = thread::scope(|s| {
    let a = s.spawn(|| left.iter().sum::<i32>());
    let b = s.spawn(|| right.iter().sum::<i32>());
    a.join().unwrap() + b.join().unwrap()
});
```

No `Arc`, no cloning. For "split this work across cores and wait", scoped
threads are usually the right tool.

## Send and Sync

Two marker traits, implemented automatically, make this all type-checked:

- `Send`: a value can be **moved** to another thread.
- `Sync`: a value can be **shared** by reference between threads (`&T` is `Send`).

Most types are both. `Rc<T>` is neither (its reference count is not atomic);
`RefCell<T>` is `Send` but not `Sync`. Try to move an `Rc` into `thread::spawn`
and you get a compile error, not a heisenbug. The next lessons show the
thread-safe alternatives: channels, `Arc` and `Mutex`.

## How many threads?

`thread::available_parallelism()` reports the usable cores. Spawning far more
CPU-bound threads than cores only adds switching overhead. In this LXC, the
learner's processes also share a process-count limit.

## Your turn

In `src/lib.rs`:

- `parallel_sum(nums, threads)`: split `nums` into at most `threads` chunks,
  sum each in a scoped thread, and add the results
- `spawn_workers(n)`: spawn `n` threads with `thread::spawn` that each return
  `"worker <i> done"`; join them and return the messages in order
- `count_matches(words, needle, threads)`: count exact matches using scoped
  threads that borrow `words` and `needle`
- `panicking_worker_is_reported()`: spawn a thread that panics and return
  `true` if `join` reported it
