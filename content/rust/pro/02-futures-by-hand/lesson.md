---
title: Futures by hand
summary: What async actually compiles to. Implement Future and Waker yourself, and write a block_on that runs one to completion.
order: 2
files: [src/lib.rs]
run: cargo test
hints:
  - "`Ready<T>` holds `Option<T>`; implement `Future` for `T: Unpin` and returns `Poll::Ready(self.0.take().unwrap())`. `Pin<&mut Self>` is awkward until you notice `self.get_mut()` works for `Unpin` types, which all of these are."
  - "`Delay::poll`: if `Instant::now() >= self.deadline` return `Ready(())`; otherwise, on the first poll, spawn a thread that sleeps until the deadline and then calls `waker.wake()`, and return `Pending`."
  - "`block_on`: build a `Waker` that unparks the current thread, `pin!` the future, then `loop { match fut.as_mut().poll(&mut cx) { Ready(v) => return v, Pending => thread::park() } }`."
  - "The waker needs a `RawWakerVTable` with clone/wake/wake_by_ref/drop functions over an `Arc<Thread>`, or build it from `std::task::Wake` with `Arc<ThreadWaker>`, which is much shorter."
---

`async fn` is not magic: the compiler turns it into a state machine that
implements `Future`. Writing the pieces by hand once makes the whole model
obvious, and explains why an async runtime is needed at all.

## The Future trait

```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}

pub enum Poll<T> { Ready(T), Pending }
```

A future does not run on its own. Something must **poll** it. Each `poll` either
finishes with `Ready(value)`, or returns `Pending` having arranged for the
**waker** in `cx` to be called when progress is possible.

The contract is: *if you return `Pending`, you must wake the waker later*, or
your future is never polled again and the program stalls.

## Pin, briefly

`async` blocks can hold references into their own state across `await` points,
so moving them in memory would dangle those pointers. `Pin<&mut Self>` says
"this will not move". Types that do not care implement `Unpin` (most hand-written
futures do), and then `self.get_mut()` gives you an ordinary `&mut Self`.

## Wakers

A `Waker` is a hand-rolled trait object: a data pointer plus a vtable of
`clone`, `wake`, `wake_by_ref` and `drop`. `std::task::Wake` builds one from an
`Arc`:

```rust
use std::sync::Arc;
use std::task::Wake;

struct ThreadWaker(std::thread::Thread);

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.0.unpark();
    }
}

let waker = Waker::from(Arc::new(ThreadWaker(thread::current())));
```

## block_on: the smallest runtime

```rust
pub fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = std::pin::pin!(future);
    let waker = Waker::from(Arc::new(ThreadWaker(thread::current())));
    let mut cx = Context::from_waker(&waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(),      // sleep until someone wakes us
        }
    }
}
```

That is a complete (single-task) async runtime. `park`/`unpark` is the handshake:
the future's timer thread calls `wake()`, which unparks this thread, which polls
again.

Real runtimes add a task queue, many tasks per thread, and an event loop
(`epoll`/`io_uring`) instead of a thread per timer. The next lesson builds the
task queue part.

## async/await on top

`async { ... }` produces a future whose `poll` resumes the state machine;
`.await` is "poll the inner future; if `Pending`, return `Pending` (remembering
where we were)". Your `block_on` runs those too, because they are just futures.

## Your turn

In `src/lib.rs`:

- `Ready<T>`: a future that is immediately ready, plus `ready(value)`
- `Delay`: a future that completes after a duration, waking the executor from a
  timer thread; `delay(duration)` builds one
- `block_on(future)`: runs any future to completion on the current thread,
  parking between polls (no busy loop)
- `Counter`: a future that returns `Pending` `n` times before returning
  `Ready(n)`, waking immediately each time; it proves the loop polls again
