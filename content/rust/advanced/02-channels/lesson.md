---
title: Channels
summary: Pass messages between threads with mpsc, build a worker pool, shut it down cleanly, and chain pipeline stages.
order: 2
files: [src/lib.rs]
run: cargo test
hints:
  - "`collect_from_producers`: create `let (tx, rx) = mpsc::channel();`, give each producer thread `tx.clone()`, then `drop(tx)` so the `for msg in rx` loop ends when every producer finishes."
  - "`WorkerPool::new`: share the receiver as `Arc<Mutex<Receiver<Job>>>`. Each worker loops `let job = rx.lock().unwrap().recv();` and exits on `Err` (the sender was dropped)."
  - "`WorkerPool::shutdown(self)`: `drop(self.sender)` first, then join every worker thread. The type `Job` is `Box<dyn FnOnce() + Send + 'static>`."
  - "`pipeline`: stage 1 thread sends numbers, stage 2 thread receives, squares and forwards, and the main thread collects. Each stage owns its sender and drops it when done."
---

"Do not communicate by sharing memory; share memory by communicating." Sending
owned values between threads through a **channel** avoids most locking entirely.

## mpsc

`std::sync::mpsc` is a **m**ulti-**p**roducer, **s**ingle-**c**onsumer channel:

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();

for id in 0..3 {
    let tx = tx.clone();                     // one sender per producer
    thread::spawn(move || {
        tx.send(format!("hello from {id}")).unwrap();
    });
}
drop(tx);                                    // drop the original sender!

for msg in rx {                              // ends when all senders are dropped
    println!("{msg}");
}
```

- `send` moves the value into the channel: ownership travels with the message.
- `recv()` blocks until a message arrives, or returns `Err` once every sender is gone.
- Iterating `rx` stops at that point, which is why the **original `tx` must be
  dropped** or the loop waits forever.

`mpsc::sync_channel(n)` has a bounded buffer: `send` blocks when it is full,
giving you back-pressure.

## A worker pool

A pool runs submitted jobs on a fixed set of threads. The jobs are boxed
closures; one channel carries them to the workers:

```rust
type Job = Box<dyn FnOnce() + Send + 'static>;
```

A `Receiver` cannot be cloned (single consumer), so the workers share it
behind `Arc<Mutex<...>>` and take turns calling `recv`. Hold the lock only
while receiving, not while running the job, or the workers run one at a time.

## Clean shutdown

Graceful shutdown falls out of channel semantics: drop the sender, each worker's
`recv` returns `Err`, the worker loop exits, and `join` returns. Implementing
shutdown in a method that takes `self` by value makes "use after shutdown"
a compile error.

## Pipelines

Chain stages, each a thread reading from one channel and writing to the next:

```text
numbers ──▶ [square] ──▶ [collect]
```

Each stage exits when its input channel closes, and drops its own sender,
which closes the next stage's input: the shutdown ripples down the pipeline.

## Your turn

In `src/lib.rs`:

- `collect_from_producers(producers, per_producer)`: `producers` threads each
  send `per_producer` values `"p<id>-<n>"`; return all messages **sorted**
- `WorkerPool::new(size)`, `execute(job)`, `shutdown(self)` which waits for all
  submitted jobs to finish; `size` must be at least 1
- `pipeline(n)`: stage 1 sends `1..=n`, stage 2 squares, the result is collected
  in order, each stage on its own thread connected by channels
