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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **share memory** vs **send values** | threads take turns with one value / each value has one owner, passed along |
| **channel** | a queue between threads |
| **sender** (`tx`) / **receiver** (`rx`) | the end that puts values in / takes them out, in order |
| **mpsc** | multi-producer, single-consumer: many senders, one receiver |
| **block** | wait until something happens, as `recv` waits for a message |
| **closed channel** | every sender dropped and the queue empty: `recv` returns `Err` |
| **hang** | a program waiting forever, often because a sender was not dropped |
| **bounded channel** | `sync_channel(n)`: room for `n` messages, `send` waits when full |
| **back-pressure** | slowing a fast producer to the consumer's speed |
| **worker pool** | a fixed set of threads fed jobs through a channel |
| **job** | a boxed closure: `Box<dyn FnOnce() + Send + 'static>` |
| **lock guard** | the value `lock()` returns; dropping it releases the lock |
| **temporary in `while let`** | lives until the end of the loop body, holding the lock too long |
| **graceful shutdown** | drop the sender, then join every worker, so queued jobs still run |
| **pipeline** | stages, each a thread, linked by channels like an assembly line |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests, which time the pool |

### Rust names

| Name | What it does |
|---|---|
| `use std::sync::mpsc;` | brings in channels |
| `let (tx, rx) = mpsc::channel();` | a new channel |
| `let tx2 = tx.clone();` | another sender |
| `tx.send(v)`, `rx.recv()` | send; wait for the next message |
| `for msg in rx { }` | receive until the channel closes |
| `drop(tx)` | drops the original sender so the loop can end |
| `mpsc::sync_channel(n)`, `tx.try_send(v)` | a bounded channel; send without waiting |
| `type Job = Box<dyn FnOnce() + Send + 'static>;` | the job type |
| `Arc<Mutex<mpsc::Receiver<Job>>>` | a receiver shared by the workers |
| `let job = rx.lock().unwrap().recv();` | receive, releasing the lock at the semicolon |
| `fn shutdown(self)` | takes the pool by value, so it cannot be used afterwards |
| `assert!(size > 0)` | panics for a pool of size 0 |

### Errors

| Error | Means |
|---|---|
| *(no error, a hang)* | a receiving loop waiting for a sender that was never dropped |
| `jobs ran one at a time` | the exercise's test message when the lock is held while running jobs |
| `SendError` | `send` after the receiver was dropped |

---

Threads that work alone need no coordination. The hard part is getting results and
instructions from one thread to another. There are two broad approaches:
let threads **share** some memory and take turns with it (lesson 3), or let
them **send** each other values, so each value has one owner at a time and
nothing is shared at all. The Go language's motto sums up the second:
"Do not communicate by sharing memory; share memory by communicating."

A **channel** is a queue between threads: one end, the **sender**, puts
values in; the other, the **receiver**, takes them out in the same order.
Sending a value **moves** it, so ownership travels with the message: the
sending thread can no longer touch it, and there is nothing for two threads
to fight over.

## mpsc

`std::sync::mpsc` is a **m**ulti-**p**roducer, **s**ingle-**c**onsumer
channel: any number of senders, exactly one receiver.

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

(A fragment.) `mpsc::channel()` returns the two ends as a tuple, by
convention named `tx` (transmit) and `rx` (receive). The type of the values,
here `String`, is worked out from what is sent.

- `tx.clone()` makes another sender for the same channel. Each producer
  thread gets its own, moved into its closure.
- `tx.send(value)` moves the value into the channel and returns at once
  (this channel's buffer has no limit). It returns `Err` only if the
  receiver no longer exists.
- `rx.recv()` **blocks**: it waits until a message arrives and returns
  `Ok(message)`. Once every sender has been dropped **and** the queue is
  empty, it returns `Err`: nothing can ever arrive again.
- `for msg in rx` calls `recv` repeatedly, and stops at that `Err`.

That last rule is why the `drop(tx)` line matters. The loop ends only when
**every** sender is gone. The three clones are dropped when their threads
finish, but the original `tx` belongs to the main thread, which is itself
sitting in the loop. Forget the `drop`, and the main thread waits for a
message from itself, forever. No error, no panic: the program hangs.
This is the most common channel bug, and the first thing to check when a
channel program freezes.

`mpsc::sync_channel(n)` makes a channel with room for only `n` messages:
`send` blocks when it is full until the receiver catches up. That gives
**back-pressure**: a fast producer is slowed to the speed of the consumer,
instead of filling memory with a growing queue. `try_send` returns `Err`
instead of waiting.

## A worker pool

Starting a thread per small task is wasteful. A **worker pool** starts a
fixed number of threads once, and feeds them tasks, **jobs**, through a
channel. Each job is a closure, boxed so that different closures can go
through the same channel (Intermediate lesson 8):

```rust
type Job = Box<dyn FnOnce() + Send + 'static>;
```

Each part of that type has a reason:

- `FnOnce()`: each job is run exactly once, so it may consume what it
  captured;
- `Send`: it will be moved to a worker thread (lesson 1);
- `'static`: the worker keeps it for an unknown time, so it must not borrow
  anything that could expire.

The pool has one channel and several workers, but a channel has only one
`Receiver`, and it cannot be cloned. So the workers **share** it, behind
`Arc<Mutex<Receiver<Job>>>`: `Arc` lets several threads own it, and `Mutex`
lets only one at a time call `recv`. (Both are explained properly in lesson
3; here it is enough that `rx.lock().unwrap()` gives one worker exclusive
use of the receiver until the lock is released.)

```text
                         ┌──> worker 1 ─┐
 execute(job) ─> tx ─> [ rx in a Mutex ] ──> worker 2   each worker: lock, recv,
                         └──> worker 3 ─┘                unlock, run the job
```

### Hold the lock only while receiving

The obvious way to write the worker loop has a subtle bug:

```rust
while let Ok(job) = rx.lock().unwrap().recv() {
    job();      // the lock is still held here!
}
```

`rx.lock().unwrap()` creates a temporary lock guard, and in a `while let`,
temporaries in the condition live until the **end of the loop body**. So the
worker keeps the receiver locked while it runs the job, and the other
workers cannot even fetch theirs. The pool has four threads, but they run
the jobs one at a time. Measured with four workers and eight jobs of 100 ms
each:

```text
while let:       800 ms     (one job at a time)
let, then run:   200 ms     (four at a time)
```

The fix is to receive in a separate statement, so the guard is dropped at
its semicolon, before the job runs:

```rust
loop {
    let job = rx.lock().unwrap().recv();    // lock, receive, unlock: all in this line
    match job {
        Ok(job) => job(),
        Err(_) => break,                    // every sender is gone: shut down
    }
}
```

The exercise's tests time the pool and fail with "jobs ran one at a time" if
the lock is held during the job.

## Clean shutdown

The channel rules give a graceful shutdown for free. Drop the sender, and
each worker's `recv` returns `Err` once the queue is empty, so every job
already submitted is still run first. The worker breaks out of its loop and
its thread ends, so `join` returns. In order:

1. drop the pool's `Sender`;
2. `join` every worker thread.

Do it the other way round and you wait for workers that are waiting for
jobs. Writing it as `fn shutdown(self)`, taking the pool **by value**, has a
bonus: after `pool.shutdown()`, `pool` has been moved, so calling
`pool.execute(...)` afterwards is a compile error, not a runtime surprise.
Inside it, `drop(self.sender);` followed by `for worker in self.workers {
worker.join().unwrap(); }` is fine: owning `self`, the method may move its
fields out one at a time.

## Pipelines

Channels chain naturally into a **pipeline**: each stage is a thread that
reads from one channel and writes to the next, like an assembly line:

```text
 stage 1: numbers ──channel──> stage 2: square ──channel──> collect
```

All stages run at the same time: while stage 2 squares the first number,
stage 1 is already sending the second. Shutdown ripples down the line on its
own. When stage 1 runs out of numbers, its thread ends and its sender is
dropped. Stage 2's `for n in num_rx` loop then ends, so its thread ends,
dropping *its* sender, and the collector's loop ends in turn. No stage needs
to know how many items there are.

## Run it

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();
    for id in 0..3 {
        let tx = tx.clone();
        thread::spawn(move || {
            tx.send(format!("hello from {id}")).unwrap();
        });
    }
    drop(tx);                                   // otherwise collect waits forever
    let mut msgs: Vec<String> = rx.iter().collect();
    msgs.sort();                                // threads finish in any order
    println!("{msgs:?}");

    let (num_tx, num_rx) = mpsc::channel();
    let (sq_tx, sq_rx) = mpsc::channel();
    thread::spawn(move || {
        for n in 1..=4 {
            num_tx.send(n).unwrap();
        }
    });
    thread::spawn(move || {
        for n in num_rx {
            sq_tx.send(n * n).unwrap();
        }
    });
    println!("{:?}", sq_rx.iter().collect::<Vec<i32>>());

    let (btx, brx) = mpsc::sync_channel::<i32>(1);
    btx.send(1).unwrap();
    println!("{}", btx.try_send(2).is_err());   // the buffer of one is full
    println!("{:?}", brx.recv());
}
```

```output
["hello from 0", "hello from 1", "hello from 2"]
[1, 4, 9, 16]
true
Ok(1)
```

The messages arrived in whatever order the threads ran, so they are sorted
before printing. The pipeline's results come out **in order**, because one
channel keeps the order of what was sent into it, and each stage is a single
thread. Its threads are never joined: the collector reads until the
channels close. The bounded channel held one message, so the second
`try_send` was refused.

## Your turn

In `src/lib.rs`:

- `collect_from_producers(producers, per_producer)`: start `producers`
  threads; thread `id` sends `per_producer` messages `"p<id>-<n>"`, `n` from
  0. Return all messages, **sorted**: `(3, 2)` gives `p0-0, p0-1, p1-0, p1-1,
  p2-0, p2-1`. With 0 producers the result is empty; it must not hang.
- `WorkerPool`:
  - `new(size)` starts `size` worker threads; `size` 0 must **panic**
    (`assert!(size > 0)`)
  - `execute(&self, job)` sends a job to the workers
  - `shutdown(self)` returns only after **every** submitted job has finished
  - jobs must run **concurrently**: the tests run eight 100 ms jobs on four
    workers and require it to take under 600 ms, so hold the receiver's
    lock only while receiving
- `pipeline(n)`: stage 1 (a thread) sends `1..=n`, stage 2 (another thread)
  squares each number and passes it on, and the function collects the
  results in order: `pipeline(5)` is `[1, 4, 9, 16, 25]`, `pipeline(0)` is
  empty
