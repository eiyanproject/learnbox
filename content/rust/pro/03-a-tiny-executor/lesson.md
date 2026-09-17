---
title: A tiny executor
summary: Many tasks on one thread. A ready queue, wakers that re-queue their task, spawning, and joining results.
order: 3
files: [src/lib.rs]
run: cargo test
hints:
  - "`Task` holds `future: Mutex<Option<BoxFuture>>` and `queue: Sender<Arc<Task>>`. `impl Wake for Task { fn wake(self: Arc<Self>) { let _ = self.queue.send(Arc::clone(&self)); } }`."
  - "`Executor::spawn(future)` boxes the future, wraps it in an `Arc<Task>` and sends it to the queue straight away, so it is polled once."
  - "`run()`: `while let Ok(task) = self.ready.try_recv()` inside an outer loop that blocks with `recv_timeout` while tasks are still outstanding; poll each task with a `Waker::from(Arc::clone(&task))`, and put the future back only when it returns Pending."
  - "`JoinHandle<T>`: share an `Arc<Mutex<Option<T>>>` between the spawned wrapper future (which stores the output) and the handle (whose `take()` reads it after `run()` returns)."
---

`block_on` runs one future. An **executor** runs many: it keeps a queue of tasks
that are ready to make progress, polls them, and goes to sleep when none are.

## The pieces

```text
spawn(future) ──▶ Task ──▶ ready queue ──▶ poll ──┬── Ready  : done
                    ▲                             └── Pending: waits for its waker
                    └────────── wake() re-queues the task ────┘
```

A **task** is a future plus the machinery to re-queue itself:

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

The waker **is** the task. Waking it just puts it back in the queue, which is
the whole trick: `Arc<T> where T: Wake` converts straight into a `Waker`.

## The loop

```rust
while let Ok(task) = queue.recv() {
    let mut slot = task.future.lock().unwrap();
    if let Some(mut future) = slot.take() {
        let waker = Waker::from(Arc::clone(&task));
        let mut cx = Context::from_waker(&waker);
        if future.as_mut().poll(&mut cx).is_pending() {
            *slot = Some(future);       // keep it for the next wake
        }                               // Ready: drop it, the task is finished
    }
}
```

Note what is **not** here: no thread per task, no locking around user data,
no polling of futures that cannot make progress. A task is polled only after
something wakes it.

## Ending the loop

`recv()` blocks forever once the queue is empty, so the executor needs to know
when everything is done: count outstanding tasks, or stop when the queue is
empty and no task is parked (`recv_timeout` plus a counter is the simple
version).

## Getting results out

Tasks are `Future<Output = ()>`, so a spawned future's value has to be handed
back another way: wrap it in an outer future that stores the output in a shared
slot, and give the caller a handle that reads that slot afterwards. Real
runtimes hand back a `JoinHandle` that is itself a future.

## What real runtimes add

Multiple worker threads with work stealing (tokio, smol), integration with the
OS event loop so I/O wakes tasks, timers, and cancellation. The core, though, is
exactly what you are about to write.

## Your turn

In `src/lib.rs`:

- `Executor::new()`, `spawn(future) -> JoinHandle<T>` for any
  `Future<Output = T> + Send + 'static`, and `run()` which polls until every
  spawned task has finished
- `JoinHandle<T>::take() -> Option<T>` for the result after `run()`
- tasks that wake each other (via the `Delay` and `Counter` style futures in the
  tests) must all complete
- `block_on(future)` for a single future, as in the previous lesson
