---
title: Atomics and lock-free code
summary: Memory ordering explained by what it forbids, compare-and-swap loops, a spin lock, and why lock-free is not automatically better.
order: 4
files: [src/lib.rs]
run: cargo test
hints:
  - "`Counter::increment`: `self.value.fetch_add(1, Ordering::Relaxed)` is enough for a statistic; nothing else depends on the order. `reset` is `swap(0, ...)`, which returns the old value."
  - "`Flag`: `set` uses `Ordering::Release` and `is_set` uses `Ordering::Acquire`, so data written before `set` is visible to a thread that sees the flag."
  - "`IdGenerator::next_id` with a maximum needs a CAS loop: `loop { let current = self.next.load(Acquire); if current >= self.max { return None } match self.next.compare_exchange_weak(current, current + 1, AcqRel, Acquire) { Ok(_) => return Some(current), Err(_) => continue } }`."
  - "`SpinLock::lock`: `while self.locked.compare_exchange_weak(false, true, Acquire, Relaxed).is_err() { std::hint::spin_loop(); }`, and `unlock` stores `false` with `Release`."
---

Advanced lesson 3 used `AtomicU64` with `Ordering::Relaxed` for a counter,
and promised an explanation of that `Ordering` argument. This lesson gives
it, and then uses atomics to build things that are usually built from locks:
a flag that safely hands data from one thread to another, an id generator
that never gives out the same id twice, and a spin lock.

A `Mutex` makes other threads **wait**. An **atomic** operation performs one
read, modify and write on a single value as one indivisible step, which no
other thread can see half-done, and nobody waits at all:

```rust
use std::sync::atomic::{AtomicUsize, AtomicBool, Ordering};

static HITS: AtomicUsize = AtomicUsize::new(0);
HITS.fetch_add(1, Ordering::Relaxed);     // add 1, as one indivisible step
HITS.load(Ordering::Relaxed);             // read
```

(A fragment.) Atomics have real advantages: they can be `static` directly,
since `AtomicUsize::new` is a `const fn`; they never put a thread to sleep;
and a single atomic operation cannot deadlock. The limit is that they only
work on one value of machine-word size or smaller: integers, `bool`, and raw
pointers. Anything bigger needs a lock, or careful lock-free design.

They are not free, though. An atomic `fetch_add` must claim the CPU cache
line holding the value away from every other core. Uncontended it costs a
few nanoseconds, many times an ordinary `+= 1`; when many cores fight over
the same value, much more, as the cache line bounces between them. Far
cheaper than a contended `Mutex`, far more expensive than nothing, so an
atomic in a tight inner loop is still worth noticing.

## Why memory ordering exists

To run fast, both the compiler and the processor **reorder** memory
operations. If you write `a = 1; b = 2;`, the compiler may emit them the
other way round, and a CPU may make the write to `b` visible to other cores
before the write to `a`. Within one thread you can never tell, because the
reordering is only done when that thread's results stay the same. **Another
thread, however, can see the difference.** Here is the classic case, one
thread preparing data and raising a flag, another waiting for the flag and
then reading the data:

```rust
// thread A                              // thread B
data = 42;                               while !ready { }
ready = true;                            println!("{data}");     // 42? or 0?
```

(Pseudo-code.) If the write to `ready` becomes visible before the write to
`data`, thread B sees the flag, reads `data`, and gets the old value, 0.
Every atomic operation therefore takes an `Ordering`, which says which
reorderings **around** it are forbidden:

| Ordering | Used on | Forbids |
|---|---|---|
| `Relaxed` | anything | nothing: the operation is atomic, but other memory may be reordered around it freely |
| `Release` | stores | moving any earlier read or write to after this store |
| `Acquire` | loads | moving any later read or write to before this load |
| `AcqRel` | read-modify-write (`fetch_add`, `compare_exchange`, `swap`) | both of the above |
| `SeqCst` | anything | as `AcqRel`, plus all `SeqCst` operations appear in one single order that every thread agrees on |

## Release and acquire: publishing data

The pattern that matters most is a **release** store paired with an
**acquire** load of the same atomic:

```rust
// thread A
payload.store(42, Ordering::Relaxed);  // no ordering of its own
ready.store(true, Ordering::Release);  // publish everything written above

// thread B
if ready.load(Ordering::Acquire) {     // if we see the flag...
    payload.load(Ordering::Relaxed)    // ...we are guaranteed to see 42
}
```

(A fragment.) The `Release` store is a fence that earlier writes cannot
cross; the `Acquire` load is a fence that later reads cannot cross. When
thread B's acquire load **reads the value** that thread A's release store
wrote, the two link up, and everything thread A did before the release is
visible to everything thread B does after the acquire:

```text
 thread A                               thread B
 payload = 42  ─┐
                │ cannot move below
 ready = true  (Release) ───────────>  ready == true  (Acquire)
                                         │ cannot move above
                                       read payload: 42, guaranteed
```

Note that `payload` itself uses `Relaxed` on both sides. It needs no
ordering of its own: the release/acquire pair on `ready` carries it along.
That is the whole trick, and it is what a `Mutex` is built from: unlocking
is a release, locking is an acquire, so whatever one thread wrote while
holding the lock is visible to the next thread that takes it.

With `Relaxed` on both sides of `ready`, thread B could see the flag and
still read the old `payload`. On x86 processors this rarely shows, because
the hardware itself reorders little; on ARM (phones, recent Macs, many
servers) it does happen. Code that "works on my machine" with the wrong
ordering is a real class of bug.

Rules of thumb:

- `Relaxed` for counters and statistics that no other data depends on;
- `Release` to publish, `Acquire` to observe, when a value signals that
  *other* data is ready;
- `SeqCst` when you are unsure. It is the strongest, and on most hardware
  only slightly slower, but its single global order is rarely what you
  actually need.

## Compare-and-swap

`fetch_add` and friends cover arithmetic. For any other update ("double it",
"add 1 unless it has reached the maximum"), the building block is
**compare-and-swap** (CAS): `compare_exchange(current, new, success,
failure)` writes `new` **only if** the value is still `current`, and tells
you whether it did:

- `Ok(previous)`: the value was `current`, and is now `new`;
- `Err(actual)`: some other thread changed it first; nothing was written,
  and `actual` is what is there now.

So the pattern is a loop: read, compute, try to swap in the result, and if
another thread got in first, retry with the new value:

```rust
let mut current = counter.load(Ordering::Relaxed);
loop {
    let next = current * 2;
    match counter.compare_exchange_weak(current, next, Ordering::AcqRel, Ordering::Relaxed) {
        Ok(_) => break,
        Err(actual) => current = actual,     // retry with what is there now
    }
}
```

(A fragment.) Two threads running this at once on the value 3: both read 3
and compute 6; one swaps 3 for 6 and succeeds; the other's swap finds 6, not
3, so it fails with `Err(6)`, computes 12, and swaps 6 for 12. No update is
lost.

The two orderings are for the two outcomes: `success` for the
read-modify-write when it succeeds, `failure` for the plain load when it
does not. `compare_exchange_weak` is allowed to fail **spuriously**, even
when the value matched; in a loop that only costs one more turn, and on some
processors (ARM) it compiles to better code. Outside a loop, use
`compare_exchange`.

## A spin lock

A lock is one `bool`: `false` when free, `true` when held. Taking it means
swapping `false` for `true`; if the swap fails, someone else holds it, so try
again:

```rust
while self.locked.compare_exchange_weak(false, true, Ordering::Acquire, Ordering::Relaxed).is_err() {
    std::hint::spin_loop();
}
// ... use the protected value ...
self.locked.store(false, Ordering::Release);
```

(A fragment.) Taking the lock is an `Acquire`, releasing it a `Release`:
exactly the publish-and-observe pairing above, so everything done inside the
lock is visible to the next holder. `std::hint::spin_loop()` tells the
processor this is a busy-wait, which saves power and helps the other
hardware thread on the same core.

This works, and is a bad idea for anything but the very shortest critical
sections: a waiting thread **spins**, burning a whole core while it waits,
and if the thread holding the lock is paused by the operating system,
everyone else spins for nothing. A `Mutex` puts waiting threads to sleep
instead, which is why it is the default.

The exercise wraps the lock in a safe API, the way `Mutex` does. The value
lives in an `UnsafeCell<T>`, the primitive that allows mutation through a
shared reference (every `Cell`, `RefCell` and `Mutex` is built on it), and
`lock()` returns a **guard**:

- the guard implements `Deref` and `DerefMut` to `T`, so `*guard += 1`
  works, and it can only exist while the lock is held;
- the guard implements `Drop`, which releases the lock, so it cannot be
  forgotten;
- getting a `&mut T` out of the `UnsafeCell` (`&mut *self.lock.value.get()`)
  is `unsafe`, and sound because the lock guarantees only one guard exists
  at a time. That is your `// SAFETY:` comment.

The starter already has the `unsafe impl Sync for SpinLock<T>`, one of the
unsafe superpowers from lesson 1: it promises the compiler that sharing a
`SpinLock` between threads is fine, which the compiler cannot work out by
itself because of the `UnsafeCell`.

## When lock-free is worth it

For counters, flags, and simple shared indexes like the id generator below:
yes, they are simple and clearly correct. For general data structures
(queues, maps), only with a strong reason. The correctness arguments get
subtle fast: the **ABA problem** (a CAS succeeds because a value changed
from A to B and back to A, hiding that something happened), and knowing when
memory removed from a lock-free structure can safely be freed. Well-tested
crates such as `crossbeam` exist for this. Measure before and after: an
uncontended `Mutex` takes only a couple of atomic operations itself.

## Run it

```rust
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;

static HITS: AtomicUsize = AtomicUsize::new(0);

fn main() {
    let handles: Vec<_> = (0..4)
        .map(|_| {
            thread::spawn(|| {
                for _ in 0..1000 {
                    HITS.fetch_add(1, Ordering::Relaxed);
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    println!("{}", HITS.load(Ordering::Relaxed));   // never a lost update

    let payload = Arc::new(AtomicU64::new(0));
    let ready = Arc::new(AtomicBool::new(false));
    let (p, r) = (Arc::clone(&payload), Arc::clone(&ready));
    let writer = thread::spawn(move || {
        p.store(42, Ordering::Relaxed);
        r.store(true, Ordering::Release);            // publish
    });
    while !ready.load(Ordering::Acquire) {           // observe
        std::hint::spin_loop();
    }
    println!("{}", payload.load(Ordering::Relaxed)); // guaranteed to be 42
    writer.join().unwrap();

    let counter = AtomicU64::new(3);
    let mut current = counter.load(Ordering::Relaxed);
    loop {
        let next = current * 2;
        match counter.compare_exchange_weak(current, next, Ordering::AcqRel, Ordering::Relaxed) {
            Ok(_) => break,
            Err(actual) => current = actual,
        }
    }
    println!("{}", counter.load(Ordering::Relaxed));
    println!(
        "{:?} {:?}",
        counter.compare_exchange(5, 0, Ordering::AcqRel, Ordering::Relaxed),
        counter.compare_exchange(6, 0, Ordering::AcqRel, Ordering::Relaxed)
    );
}
```

```output
4000
42
6
Err(6) Ok(6)
```

4 threads × 1000 increments with no lost update. The main thread spun until
it saw the flag, and the release/acquire pair guaranteed it then saw 42. The
CAS loop doubled 3 to 6. The last line: swapping `5` for 0 failed, handing
back the value it actually found, 6, which is what a retry loop uses; then
swapping `6` for 0 succeeded, returning the previous value.

## Your turn

In `src/lib.rs`:

- `Counter`, lock-free, all methods taking `&self`:
  - `increment()` and `add(n)`
  - `get()`, the current value
  - `reset()`, which sets it to 0 and **returns the value it had** (`swap`
    does both in one atomic step, so no increment in between is lost)
- `Flag`: `set()` and `is_set()`, with `Release` in `set` and `Acquire` in
  `is_set`
- `IdGenerator::new(start, max)` (given): `next_id() -> Option<u64>` returns
  `start`, `start + 1`, ... up to but not including `max`, then `None`
  forever. With 8 threads drawing ids at once, no id may be handed out twice
  and none may reach `max`. `fetch_add` alone would overshoot past `max`, so
  use a compare-and-swap loop: check the limit, then try to claim the id.
- `SpinLock<T>`: `lock()` returns a guard (a struct you define, such as
  `SpinGuard<'a, T>`) that implements `Deref<Target = T>`, `DerefMut`, and
  `Drop` to unlock. 4 threads each adding 1 to the value 20,000 times must
  end at 80,000. Give the `unsafe` blocks in the guard `// SAFETY:` comments.

The tests read your source to check that `Ordering::Release`,
`Ordering::Acquire` and `compare_exchange` appear in it.
