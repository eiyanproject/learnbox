---
title: Shared state
summary: Arc for shared ownership across threads, Mutex and RwLock for mutation, atomics for counters, and avoiding deadlocks.
order: 3
files: [src/lib.rs]
run: cargo test
hints:
  - "`BankAccount` wraps `Arc<Mutex<i64>>`; `Clone` is derived, so every clone shares the same balance. `withdraw` locks once and checks and subtracts under that single lock."
  - "`HitCounter` uses `Arc<AtomicU64>`: `hit` is `self.hits.fetch_add(1, Ordering::Relaxed)` and `total` is `load`."
  - "`ConfigStore` wraps `Arc<RwLock<HashMap<String, String>>>`: `get` uses `.read()`, `set` uses `.write()`."
  - "`transfer(from, to, amount)` must lock both accounts in a consistent order (by `id`) to avoid deadlock, then check the balance and move the money while holding both locks."
---

Channels move data between threads. When several threads really need to see
and change the **same** data, you share it.

## Arc: Rc for threads

`Arc<T>` (atomically reference counted) is the thread-safe version of `Rc`:
cloning it is cheap, and the value lives until the last clone is dropped.

```rust
use std::sync::Arc;
use std::thread;

let config = Arc::new(load_config());
for _ in 0..4 {
    let config = Arc::clone(&config);
    thread::spawn(move || use_config(&config));
}
```

Like `Rc`, `Arc` gives only shared (`&`) access.

## Mutex: one at a time

```rust
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
let handles: Vec<_> = (0..8).map(|_| {
    let counter = Arc::clone(&counter);
    thread::spawn(move || {
        *counter.lock().unwrap() += 1;         // lock() returns a guard
    })
}).collect();
```

- `lock()` blocks until the mutex is free, and returns a `MutexGuard` that
  derefs to the data. The lock is released when the guard is dropped.
- The data is **inside** the mutex. There is no way to reach it without locking,
  which is the whole point.
- `lock()` returns `Err` if another thread panicked while holding the lock
  ("poisoned"); `.unwrap()` is common when that should never happen.

Keep the critical section to one logical operation. Checking a balance in one
lock and subtracting in a second lock lets another thread slip in between.

## RwLock: many readers or one writer

```rust
use std::sync::RwLock;

let settings = RwLock::new(HashMap::new());
settings.read().unwrap().get("theme");        // many readers at once
settings.write().unwrap().insert(k, v);       // exclusive
```

Worth it when reads vastly outnumber writes.

## Atomics: lock-free counters and flags

For a single integer or bool, atomic types avoid locks altogether:

```rust
use std::sync::atomic::{AtomicU64, Ordering};

static REQUESTS: AtomicU64 = AtomicU64::new(0);
REQUESTS.fetch_add(1, Ordering::Relaxed);
```

(`Ordering` here is about CPU memory ordering, not sorting; `Relaxed` is fine for
statistics. The Pro track goes deeper.)

## Deadlocks

Thread A locks `x` then waits for `y`; thread B locks `y` then waits for `x`.
Both wait forever. The standard cure is a **global lock order**: whenever you
need several locks, always take them in the same order (by id, by address).

Rust prevents data races at compile time, but not deadlocks.

## Your turn

In `src/lib.rs`:

- `BankAccount` (cloneable handle to one shared account): `new(id, balance)`,
  `deposit`, `withdraw` (returns `false` and changes nothing if funds are
  insufficient), `balance`
- `transfer(from, to, amount)`: atomic with respect to both accounts; returns
  `false` if `from` lacks funds; must not deadlock when two threads transfer in
  opposite directions at the same time
- `HitCounter`: cloneable, lock-free `hit()` and `total()`
- `ConfigStore`: cloneable `get(key) -> Option<String>` and `set(key, value)` backed by `RwLock`
