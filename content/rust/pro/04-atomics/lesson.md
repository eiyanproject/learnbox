---
title: Atomics and lock-free code
summary: Memory ordering explained by what it forbids, compare-and-swap loops, a spin lock, and why lock-free is not automatically better.
order: 4
files: [src/lib.rs]
run: cargo test
hints:
  - "`Counter::increment`: `self.value.fetch_add(1, Ordering::Relaxed)` is enough for a statistic; nothing else depends on the order."
  - "`Flag`: `set` uses `Ordering::Release` and `is_set` uses `Ordering::Acquire`, so data written before `set` is visible to a thread that sees the flag."
  - "`IdGenerator::next_id` with a maximum needs a CAS loop: `loop { let current = self.next.load(Acquire); if current >= self.max { return None } match self.next.compare_exchange_weak(current, current + 1, AcqRel, Acquire) { Ok(_) => return Some(current), Err(_) => continue } }`."
  - "`SpinLock::lock`: `while self.locked.compare_exchange_weak(false, true, Acquire, Relaxed).is_err() { std::hint::spin_loop(); }`, and `unlock` stores `false` with `Release`."
---

A `Mutex` makes other threads wait. **Atomic** operations instead perform a
single indivisible read-modify-write on one value, with no waiting at all.

```rust
use std::sync::atomic::{AtomicUsize, AtomicBool, Ordering};

static HITS: AtomicUsize = AtomicUsize::new(0);
HITS.fetch_add(1, Ordering::Relaxed);
HITS.load(Ordering::Relaxed);
```

Atomics can be `static` without `lazy_static`, need no syscall and never block,
and a single operation cannot deadlock. They only work on single machine-word
values.

They are not free, though. An uncontended `fetch_add` is around **twenty times**
the cost of an ordinary `+= 1`, because it still has to lock the cache line
against other cores. That is far cheaper than a `Mutex`, and far more expensive
than nothing - so an atomic in a tight inner loop is still worth noticing.

## Memory ordering

Compilers and CPUs reorder memory operations for speed. Ordering says which
reorderings are forbidden **around** an atomic operation:

| Ordering | Meaning |
|---|---|
| `Relaxed` | atomic, but no ordering guarantees about other memory |
| `Acquire` (loads) | nothing after this load can move before it |
| `Release` (stores) | nothing before this store can move after it |
| `AcqRel` | both, for read-modify-write operations |
| `SeqCst` | as above, plus one global order all threads agree on |

The pattern that matters is **release/acquire pairing**:

```rust
// thread A
payload.store(42, Ordering::Relaxed);  // no ordering of its own
ready.store(true, Ordering::Release);  // publish everything written above

// thread B
if ready.load(Ordering::Acquire) {     // if we see the flag...
    payload.load(Ordering::Relaxed)    // ...we are guaranteed to see 42
}
```

Note that `payload` is written and read with `Relaxed`. It does not need an
ordering of its own: the `Release` store and the `Acquire` load are what create
the guarantee, and everything thread A wrote *before* its release comes along
with it. That is the whole trick, and it is what a `Mutex` is built from.

With `Relaxed` on both sides, thread B could see the flag but not the data.

Rules of thumb: `Relaxed` for counters nobody synchronises on; `Release`/`Acquire`
to publish and observe data; `SeqCst` when you are unsure (it is the safest and
slowest).

## Compare-and-swap

`compare_exchange(current, new, success, failure)` writes `new` only if the value
is still `current`. When it is not, someone else changed it, and you retry:

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

This is how any "atomic update that is not just add" is written. Use
`compare_exchange_weak` in loops: it may fail spuriously but compiles to better
code on some architectures.

## A spin lock

```rust
while self.locked.compare_exchange_weak(false, true, Ordering::Acquire, Ordering::Relaxed).is_err() {
    std::hint::spin_loop();
}
```

Correct, and a bad idea for anything but the very shortest critical sections: a
spinning thread burns a core, and can keep the lock holder from being scheduled.
`Mutex` parks the thread instead, which is why it is the default.

## When lock-free is worth it

Counters, flags, and simple shared indexes: yes. General data structures: only
with strong reason, since correctness arguments get subtle fast (the ABA
problem, memory reclamation). Measure before and after; an uncontended `Mutex`
is already very fast.

## Your turn

In `src/lib.rs`:

- `Counter`: `increment`, `add(n)`, `get`, `reset`, all lock-free
- `Flag`: `set()` and `is_set()` with release/acquire pairing
- `IdGenerator::new(start, max)`: `next_id() -> Option<u64>` handing out unique
  ids up to (not including) `max`, with a CAS loop; never hands out a duplicate
- `SpinLock<T>`: `lock()` returning a guard that derefs to `T` and unlocks on drop
