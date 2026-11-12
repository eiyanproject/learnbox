---
title: A tiny executor
summary: Many tasks on one thread. A ready queue, wakers that re-queue their task, spawning, and joining results.
order: 3
files: [src/lib.rs]
run: cargo test
hints:
  - "`Task` holds `future: Mutex<Option<BoxFuture>>` and `queue: Sender<Arc<Task>>`. `impl Wake for Task { fn wake(self: Arc<Self>) { let _ = self.queue.send(Arc::clone(&self)); } }`."
  - "`Executor::spawn(future)` boxes the future, wraps it in an `Arc<Task>` and sends it to the queue straight away, so it is polled once."
  - "`run()`: loop while a counter of unfinished tasks is above 0, taking tasks with `recv_timeout` so the loop can check the counter again while every task is waiting; poll each task with a `Waker::from(Arc::clone(&task))`, put the future back only when it returns Pending, and decrement the counter when it is Ready."
  - "`JoinHandle<T>`: share an `Arc<Mutex<Option<T>>>` between the spawned wrapper future (which stores the output) and the handle (whose `take()` reads it after `run()` returns)."
---

Lesson 2's `block_on` runs **one** future, and its thread sleeps whenever
that future is waiting. The point of async is to do better: while one task
waits for a timer or the network, run another. An **executor** does that. It
keeps a queue of tasks that are ready to make progress, polls them one after
another, and only sleeps when **none** of them can move.

This lesson builds one, small but complete, on a single thread. It is the
core of what runtimes like `tokio` do, without their extra machinery.

## The pieces

```text
 spawn(future) ──> Task ──> ready queue ──> run() polls it ──┬── Ready:   finished, drop it
                     ^                                       └── Pending: set aside
                     │                                               │
                     └──── its waker is called: back into the queue ─┘
```

A **task** is a spawned future, plus what it needs to get itself back into
the queue when woken:

```rust
type BoxFuture = Pin<Box<dyn Future<Output = ()> + Send>>;

struct Task {
    future: Mutex<Option<BoxFuture>>,
    queue: Sender<Arc<Task>>,
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        let _ = self.queue.send(Arc::clone(&self));
    }
}
```

Why each part of `Task` is the way it is:

- `BoxFuture`: different `async` blocks are different types, so the queue
  holds them as boxed trait objects (Advanced lesson 10). `Pin<Box<...>>`
  pins each one on the heap (lesson 2), where it stays while it is polled
  over and over. `Send`, because a waker may be called from another thread,
  such as a timer thread, and it carries the task with it.
- `Mutex<Option<...>>`: the task is shared through an `Arc`, so changing it
  needs interior mutability, and the `Mutex` makes that thread-safe. The
  `Option` lets `run` **take** the future out to poll it, and put it back
  only if it is not finished; `None` then means "this task is done", so a
  stray late wake-up does nothing.
- `queue: Sender<Arc<Task>>`: a sender for the executor's ready queue, a
  channel (Advanced lesson 2).

The key idea is in `impl Wake for Task`: **the waker is the task itself**.
Lesson 2's waker unparked a thread; this one sends the task back into the
ready queue. Since the standard library converts any `Arc<T>` where `T:
Wake` into a `Waker`, `Waker::from(Arc::clone(&task))` is the whole waker.

## The loop

Polling a task looks like this:

```rust
let mut slot = task.future.lock().unwrap();
if let Some(mut future) = slot.take() {
    let waker = Waker::from(Arc::clone(&task));
    let mut cx = Context::from_waker(&waker);
    if future.as_mut().poll(&mut cx).is_pending() {
        *slot = Some(future);       // keep it for the next wake
    }                               // Ready: drop it, the task is finished
}
```

(A fragment.) Notice what is **not** here: no thread per task, and no
polling of a task that cannot make progress. A task is polled once when it is
spawned, and after that only when something has called its waker. If the
future returns `Pending`, it has handed its waker to whatever it waits for
(lesson 2's contract), and the executor forgets about it until that waker
puts it back in the queue.

## Ending the loop

When should `run` return? "When the queue is empty" sounds right, and works
for tasks that wake themselves at once, as in the program below. It is wrong
in general. A task waiting for a timer is not in the queue: it sits inside
the timer thread's waker until the time is up. An empty queue therefore
means either "all done" or "everyone is waiting", and returning in the
second case would abandon those tasks.

The executor cannot wait for the channel to close either, because it holds a
`Sender` itself (for `spawn`), so the channel never closes. The simple,
reliable answer is to **count**: add 1 for each spawned task, subtract 1
when a task returns `Ready`, and loop while the count is above 0. While all
tasks are waiting, the loop blocks on the queue; `recv_timeout` (rather than
`recv`) lets it wake now and then to check the count again.

## Getting results out

A task's future has `Output = ()`, so that tasks producing different types
can share one queue. To return a value from a spawned future anyway, wrap it
in an outer future that stores the value in a shared slot:

```rust
let slot = Arc::new(Mutex::new(None));
let result = Arc::clone(&slot);
let wrapped: BoxFuture = Box::pin(async move {
    *result.lock().unwrap() = Some(future.await);   // run the user's future, keep its value
});
```

(A fragment.) The caller gets a handle holding the other `Arc` to the same
slot, and after `run()` reads the value out of it. That is the exercise's
`JoinHandle<T>`. (In real runtimes, a `JoinHandle` is itself a future that
you `.await`.)

## Run it

A two-task executor in one program, without timers, results or a task count.
`YieldNow` is a future that returns `Pending` once, waking itself straight
away: "let the other tasks have a turn".

```rust
use std::future::Future;
use std::pin::Pin;
use std::sync::mpsc::{channel, Sender};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};

type BoxFuture = Pin<Box<dyn Future<Output = ()> + Send>>;

struct Task {
    future: Mutex<Option<BoxFuture>>,
    queue: Sender<Arc<Task>>,
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        let _ = self.queue.send(Arc::clone(&self));
    }
}

/// Pending once, waking itself straight away: "let the others have a turn".
struct YieldNow(bool);

impl Future for YieldNow {
    type Output = ();
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        if this.0 {
            return Poll::Ready(());
        }
        this.0 = true;
        cx.waker().wake_by_ref();
        Poll::Pending
    }
}

async fn worker(name: &'static str, steps: u32) {
    for i in 0..steps {
        println!("{name} step {i}");
        YieldNow(false).await;
    }
    println!("{name} done");
}

fn main() {
    let (queue, ready) = channel::<Arc<Task>>();
    for (name, steps) in [("a", 3), ("b", 2)] {
        let future: BoxFuture = Box::pin(worker(name, steps));
        let task = Arc::new(Task { future: Mutex::new(Some(future)), queue: queue.clone() });
        queue.send(task).unwrap();
    }

    let mut polls = 0;
    // Stops when the queue is empty: fine here, because every Pending task
    // has already re-queued itself. A task waiting on a timer would be lost.
    while let Ok(task) = ready.try_recv() {
        polls += 1;
        let mut slot = task.future.lock().unwrap();
        if let Some(mut future) = slot.take() {
            let waker = Waker::from(Arc::clone(&task));
            let mut cx = Context::from_waker(&waker);
            if future.as_mut().poll(&mut cx).is_pending() {
                *slot = Some(future);
            }
        }
    }
    println!("{polls} polls");
}
```

```output
a step 0
b step 0
a step 1
b step 1
a step 2
b done
a done
7 polls
```

The two tasks take turns on one thread. Each `YieldNow(false).await` returns
`Pending` after putting its task at the **back** of the queue, so the other
task runs next. Counting polls: task `a` was polled 4 times (3 steps, then
the poll that finished it), `b` 3 times. `try_recv` returns `Err` as soon as
the queue is empty, which here happens only after both have finished.

## What real runtimes add

Multiple worker threads, with idle threads **stealing** tasks from busy
ones' queues (`tokio`, `smol`); integration with the operating system's
event loop, so that a socket becoming readable wakes the task waiting on it,
without a thread per wait; timers managed in one place instead of a thread
each; and cancellation, by dropping a task's future. The core, a queue of
woken tasks and a loop that polls them, is exactly what you are about to
write.

## Your turn

In `src/lib.rs` (`Delay`, the timer future from lesson 2, is provided):

- `Executor::new()`
- `spawn(&self, future) -> JoinHandle<T>`, for any
  `Future<Output = T> + Send + 'static`: wrap the future so its output is
  stored for the handle, box it into a task, and queue it straight away so
  it is polled at least once
- `run(&self)`: polls until **every** spawned task has finished, including
  tasks that spend most of their time waiting for a `Delay`, and then
  returns. With nothing spawned, it returns at once.
- the tasks must really run **concurrently**: the tests spawn 8 tasks that
  each wait 150 ms, and require the whole run to take under 900 ms. Never
  block the executor's thread on one task (no sleeping in `run` while there
  is work in the queue).
- tasks finish in the order their wake-ups arrive: three tasks waiting 90,
  60 and 30 ms finish in the order 30, 60, 90
- `JoinHandle<T>::take()` (given) returns the result once after `run()`,
  then `None`
- `block_on(future)`, as in lesson 2, which must still work on its own; the
  starter imports `thread`, so lesson 2's `ThreadWaker` fits here
