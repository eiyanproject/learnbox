---
title: Futures by hand
summary: What async actually compiles to. Implement Future and Waker yourself, and write a block_on that runs one to completion.
order: 2
files: [src/lib.rs]
run: cargo test
hints:
  - "`Ready<T>` holds `Option<T>`; implement `Future` for `T: Unpin` and return `Poll::Ready(self.get_mut().0.take().unwrap())`. `Pin<&mut Self>` is awkward until you notice `self.get_mut()` works for `Unpin` types, which all of these are."
  - "`Delay::poll`: if `Instant::now() >= self.deadline` return `Ready(())`; otherwise, on the first poll, spawn a thread that sleeps until the deadline and then calls `waker.wake()`, and return `Pending`."
  - "`block_on`: build a `Waker` that unparks the current thread, `pin!` the future, then `loop { match fut.as_mut().poll(&mut cx) { Ready(v) => return v, Pending => thread::park() } }`."
  - "The waker needs a `RawWakerVTable` with clone/wake/wake_by_ref/drop functions over an `Arc<Thread>`, or build it from `std::task::Wake` with `Arc<ThreadWaker>`, which is much shorter."
---

Threads (Advanced track) let a program wait for several things at once, but
each thread costs memory and switching time, and a server handling ten
thousand connections cannot afford ten thousand threads that mostly sit
waiting for the network. **Async** Rust is the alternative: many tasks share
a few threads, and a task that would wait **steps aside** so another can
run.

`async fn` and `.await` make this look like ordinary code, but there is no
magic underneath. The compiler turns each `async` function into a **state
machine**, a value that implements the `Future` trait, and something called
an **executor** or **runtime** drives it. Rust's standard library includes
the trait but no runtime; crates such as `tokio` provide one. Writing the
pieces by hand once, in this lesson, makes the whole model clear, and shows
why a runtime is needed at all.

## The Future trait

```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}

pub enum Poll<T> {
    Ready(T),
    Pending,
}
```

(The standard library's definitions.) A **future** is a value representing
work that will finish later with an `Output`. The important part: **a future
does nothing on its own**. Creating one runs no code. Something must
**poll** it, by calling `poll`, and each call does one of two things:

- finishes, returning `Poll::Ready(value)`;
- or cannot finish yet (the data has not arrived, the timer has not run
  out), and returns `Poll::Pending`.

Polling again and again until it is ready would work, but would keep a CPU
core busy doing nothing useful. Instead, `poll` receives a **context**
`cx`, holding a **waker**: a handle the future can use to say "poll me
again now, there is progress to make". This is the contract every future
must keep:

> If you return `Pending`, you must make sure the waker is called later.

A future that returns `Pending` without arranging a wake is never polled
again, and whatever waits for it waits forever. There is no error and no
panic: the program stops making progress.

```text
 executor                          future
   │── poll(cx) ─────────────────────>│  not ready: give cx.waker() to a timer,
   │<──────────────────────── Pending │  an I/O watcher, another thread...
   │  (sleeps)                        │
   │<─────────── waker.wake() ────────│  ...which calls it when there is progress
   │── poll(cx) ─────────────────────>│
   │<───────────────────── Ready(42) ─│
```

## Pin, briefly

The odd-looking receiver `self: Pin<&mut Self>` exists because of what
`async` blocks compile to. An `async` block can keep a reference to one of
its own local variables across an `.await`:

```rust
async {
    let data = [1, 2, 3];
    let first = &data[0];        // points into this future's own state
    some_io().await;             // suspended here: data and first are stored in the future
    println!("{first}");
}
```

(A fragment.) While suspended, `data` and `first` are stored inside the
future value itself, and `first` points at `data`. If the future were
**moved** to another place in memory, `first` would still point at the old
place. `Pin<&mut Self>` is a promise that the future will not be moved from
now on, which makes such self-references safe.

For hand-written futures that hold no self-references, which is all of this
lesson's, moving is harmless. Such types implement the auto trait `Unpin`
("fine to move even when pinned"), and for them `self.get_mut()` turns the
`Pin<&mut Self>` back into an ordinary `&mut Self`. Almost every type is
`Unpin`; the futures generated from `async` blocks are the main exception.

## Wakers

A `Waker` is the handle that lets a future ask to be polled again. What
"wake" means is up to the executor: in a single-threaded `block_on` (below),
it means "un-pause the thread that is waiting"; in a full runtime, "put this
task back on the run queue".

Under the hood a `Waker` is a hand-made trait object: a data pointer plus a
table of four functions (`clone`, `wake`, `wake_by_ref`, `drop`), a
`RawWakerVTable`. Building one by hand means writing those four functions
with raw pointers. The standard library offers a much shorter, safe way: the
`Wake` trait. Implement it for a struct, wrap that in an `Arc`, and convert:

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

(A fragment.) `thread::current()` is a handle to the running thread. The
waker owns a copy, and calling `wake` on the waker calls `unpark` on that
thread.

`thread::park()` and `unpark()` are a simple handshake between threads:
`park` puts the current thread to sleep until some other thread calls
`unpark` on it. If `unpark` happens first, the next `park` returns at once,
so a wake that arrives "too early" is not lost. (`park` may also return
without any `unpark`, a **spurious** wake-up, which is harmless here because
the loop below polls again.)

## block_on: the smallest runtime

With those pieces, an executor that runs one future to completion on the
current thread is a few lines:

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

Line by line:

1. `std::pin::pin!(future)` pins the future in place, on this function's
   stack, giving a `Pin<&mut F>`. It is not moved again until `block_on`
   returns.
2. The waker, when called from anywhere, unparks **this** thread.
3. `Context::from_waker` wraps it in the `cx` that `poll` expects.
4. The loop polls. `as_mut()` re-borrows the pin for each call. On
   `Ready`, the value is returned. On `Pending`, the thread **parks**, using
   no CPU, until the future's wake arrives, then polls again.

That is a complete, if single-task, async runtime. The tests check that your
source mentions `park`: a version that loops without parking would also give
the right answers, but would burn a CPU core while waiting.

Real runtimes add three things: a **queue of tasks**, so one thread can run
many futures and poll whichever was woken (the next lesson builds that); an
**event loop** using the operating system's `epoll` or `io_uring`, so one
thread can wait on thousands of sockets instead of a thread per timer; and
**multiple worker threads**.

## async/await on top

`async { ... }` and `async fn` produce futures whose `poll` runs the code up
to the next `.await` that is not ready. `x.await`, inside one, means:

```text
loop {
    match x.poll(cx) {               // the outer future's own cx is passed in
        Ready(v) => break v,         // carry on with the value
        Pending => return Pending,   // suspend; remember we were at this .await
    }
}
```

(A sketch of the generated code.) The waker passed to the inner future is
the outer future's own waker, so when the inner future wakes, it is the
**outer** task that gets polled again, which then polls the inner one. So
your `block_on` can run `async` blocks and `async fn` calls without knowing
anything about them: to it, they are futures like any other.

## Run it

```rust
use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::time::Duration;

struct ThreadWaker(thread::Thread);

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.0.unpark();
    }
}

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = std::pin::pin!(future);
    let waker = Waker::from(Arc::new(ThreadWaker(thread::current())));
    let mut cx = Context::from_waker(&waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(),
        }
    }
}

/// Pending `remaining` times - each time arranging a wake from a timer
/// thread - then Ready with the number of polls it took.
struct CountDown {
    remaining: u32,
    polls: u32,
}

impl Future for CountDown {
    type Output = u32;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<u32> {
        let this = self.get_mut();
        this.polls += 1;
        if this.remaining == 0 {
            return Poll::Ready(this.polls);
        }
        this.remaining -= 1;
        let waker = cx.waker().clone();
        thread::spawn(move || {
            thread::sleep(Duration::from_millis(5));
            waker.wake();                  // the contract: Pending, then a wake
        });
        Poll::Pending
    }
}

fn main() {
    println!("{}", block_on(CountDown { remaining: 3, polls: 0 }));
    let answer = block_on(async {
        let a = async { 20 }.await;        // async blocks are just futures
        a + 22
    });
    println!("{answer}");
}
```

```output
4
42
```

Three `Pending`s and a `Ready`: four polls, each after a wake from a timer
thread. `cx.waker().clone()` is needed because the waker must be moved into
the thread, while `cx` only lends it. Delete the `waker.wake()` line and the
program hangs at the first `Pending`: the contract, broken. The `async`
block's inner `async { 20 }` was ready at its first poll, so the whole block
finished in one poll.

## Your turn

In `src/lib.rs`:

- `Ready<T>`, built by `ready(value)`: a future that is ready at its first
  poll, returning the value. It stores an `Option<T>` so `poll` can `take()`
  the value out. Implement `Future` for `Ready<T>` where `T: Unpin`.
- `Delay`, built by `delay(duration)`: a future that finishes (`Ready(())`)
  once its deadline has passed. On the first poll before the deadline, start
  a timer thread that sleeps until the deadline and then calls the waker, and
  return `Pending`; use the `started` field so later polls do not start more
  threads. The tests check that a 150 ms delay takes at least 140 ms.
- `Counter`, built by `counter(n)`: returns `Pending` `n` times, waking
  itself **immediately** each time (`cx.waker().wake_by_ref()`), then
  returns `Ready` with the **number of times it was polled**, which is
  `n + 1`: `counter(5)` gives 6, `counter(0)` gives 1. It shows that your
  loop polls again after a wake.
- `block_on(future)`: runs any future to completion on the current thread,
  **parking** between polls, as above. The tests also run `async` blocks
  and nested `async fn`s that `.await` your three futures.
