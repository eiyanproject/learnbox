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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **shared state** | one value several threads see and change |
| **`Arc<T>`** | atomically reference counted: `Rc` for threads |
| **atomic operation** | one the processor guarantees cannot be interrupted halfway |
| **clone, then move** | each thread gets its own `Arc` handle |
| **mutex** (mutual exclusion) | a lock around a value; one thread at a time |
| **`MutexGuard`** | acts like `&mut` to the value; dropping it unlocks |
| **data inside the lock** | the only way to reach the value is through `lock()` |
| **poisoned** | a thread panicked while holding the lock; `lock()` returns `Err` |
| **race condition** | a logic bug where timing changes the result, such as check-then-act across two locks |
| **check and change under one lock** | hold the guard for the whole operation |
| **`RwLock`** | many readers or one writer |
| **atomic types** | `AtomicU64`, `AtomicUsize`, `AtomicBool`: lock-free numbers and flags |
| **`Ordering`** | how an atomic operation is ordered relative to others; `Relaxed` is enough for counters |
| **deadlock** | two threads each waiting for a lock the other holds, forever |
| **global lock order** | always take several locks in the same order, such as by id |
| **cloneable handle** | a struct holding an `Arc`, so clones share the same state |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests, which hammer the account from many threads |

### Rust names

| Name | What it does |
|---|---|
| `use std::sync::{Arc, Mutex, RwLock};` | bring them in |
| `let c = Arc::clone(&counter);` | another handle |
| `*counter.lock().unwrap() += 1` | lock, change, unlock at the semicolon |
| `let mut balance = self.balance.lock().unwrap();` | a named guard: locked until the end of the function |
| `lock.read().unwrap()`, `lock.write().unwrap()` | an `RwLock` read / write guard |
| `use std::sync::atomic::{AtomicU64, Ordering};` | atomics |
| `hits.fetch_add(1, Ordering::Relaxed)`, `hits.load(Ordering::Relaxed)` | add one; read |
| `Arc::strong_count(&a)` | how many handles exist |
| `#[derive(Clone)] struct BankAccount { id: u32, inner: Arc<Mutex<u64>> }` | one shape for a shared account |
| `if from.id < to.id { lock from, then to } else { lock to, then from }` | lock in id order |

### Errors

| Error | Means |
|---|---|
| `error[E0382]: borrow of moved value: counter` | moved the `Arc` itself instead of a clone |
| `PoisonError` | locking a mutex a panicked thread held |
| *(no error, a hang)* | a deadlock from locks taken in different orders |

---

Channels (lesson 2) move values between threads, so each value has one
owner at a time. Some data does not fit that model: a bank balance that many
threads deposit into, a counter of requests served, settings every thread
reads. Several threads need to see and change **the same** value. This
lesson covers the tools for that, which mirror the single-threaded ones from
Intermediate lesson 5:

| Single-threaded | Thread-safe | Job |
|---|---|---|
| `Rc<T>` | `Arc<T>` | several owners of one value |
| `RefCell<T>` | `Mutex<T>`, `RwLock<T>` | change a value through a shared reference |
| `Cell<i32>` and friends | `AtomicU64` and friends | change one number without any lock |

The thread-safe versions cost a little more, and the compiler's `Send` and
`Sync` checks (lesson 1) make sure you cannot use the cheaper ones by
mistake.

## Arc: Rc for threads

`Arc<T>` (**a**tomically **r**eference **c**ounted) is the thread-safe
version of `Rc`. It updates its counter with **atomic** operations, which
the processor guarantees cannot be interrupted halfway, so two threads
cloning at the same time can never lose a count. Like `Rc`, cloning it is
cheap and shares the value, and the value is dropped when the last clone is:

```rust
use std::sync::Arc;
use std::thread;

let config = Arc::new(load_config());
for _ in 0..4 {
    let config = Arc::clone(&config);     // one handle per thread
    thread::spawn(move || use_config(&config));
}
```

(A fragment.) The pattern, clone first and then `move` the clone in, is how
every thread gets its own owning handle. Why not `move` the value
itself? Because only one thread could own it then:

```text
error[E0382]: borrow of moved value: `counter`
  |
4 |     let counter = Mutex::new(0);
  |         ------- move occurs because `counter` has type `std::sync::Mutex<i32>`, which does not implement the `Copy` trait
5 |     let h = thread::spawn(move || { *counter.lock().unwrap() += 1; });
  |                           -------    ------- variable moved due to use in closure
...
7 |     println!("{}", counter.lock().unwrap());
  |                    ^^^^^^^ value borrowed here after move
```

Like `Rc`, `Arc` gives only shared (`&`) access to the value inside.
Changing it needs one of the types below. (Scoped threads, lesson 1, can
borrow without `Arc`; `Arc` is for `thread::spawn` and for data that must
outlive any one function.)

## Mutex: one thread at a time

A **mutex** (from **mut**ual **ex**clusion) is a lock around a value: a
thread must **lock** it to reach the value, and only one thread can hold the
lock at a time. The others wait in `lock()` until it is released.

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

(A fragment.) What happens on that line:

1. `counter.lock()` waits until no other thread holds the lock, then takes
   it, and returns a `MutexGuard`, which acts like `&mut` to the number
   inside.
2. `*... += 1` changes the number through the guard.
3. The guard is a temporary, dropped at the end of the statement, and
   **dropping the guard releases the lock**. You never unlock by hand, so you
   cannot forget to.

Rust's design has one big difference from mutexes in most languages: the
data is **inside** the mutex. In C or Java, a lock and the data it protects
are separate things, and nothing stops code from touching the data without
taking the lock. Here there is no way to reach the number except through
`lock()`.

`lock()` returns a `Result`. It is `Err` if another thread **panicked**
while holding this lock, which may have left the data half-updated; the
mutex is then called **poisoned**. `.unwrap()` turns that into a panic in
this thread too, which is the usual choice when it should never happen.

### Hold the lock for the whole operation

A mutex only protects what happens *while you hold it*. This `withdraw` is
broken, even though every access is locked:

```rust
fn withdraw(&self, amount: i64) -> bool {
    if *self.balance.lock().unwrap() >= amount {      // lock 1: check, unlock
        *self.balance.lock().unwrap() -= amount;      // lock 2: subtract, unlock
        true
    } else {
        false
    }
}
```

Two threads withdrawing 80 from a balance of 100 can interleave like this:

| Thread A | Thread B | Balance |
|---|---|---|
| lock, see 100 ≥ 80, unlock | | 100 |
| | lock, see 100 ≥ 80, unlock | 100 |
| lock, subtract 80, unlock | | 20 |
| | lock, subtract 80, unlock | **-60** |

Both checks passed before either subtraction. This is called a **race
condition** (not a data race: there was no unsynchronised access, so the
compiler cannot catch it), and the fix is to check and change under **one**
lock:

```rust
fn withdraw(&self, amount: i64) -> bool {
    let mut balance = self.balance.lock().unwrap();   // locked until `balance` is dropped
    if *balance < amount {
        return false;
    }
    *balance -= amount;
    true
}
```

Naming the guard (`let mut balance = ...`) keeps the lock held until the
end of the function. The exercise's tests run ten threads withdrawing at
once and check that exactly the available money is paid out.

## RwLock: many readers or one writer

A `Mutex` lets one thread in at a time, even if all of them only want to
read. An `RwLock` (read-write lock) has the same rule as borrowing: **many
readers, or one writer**:

```rust
use std::sync::RwLock;

let settings = RwLock::new(HashMap::new());
settings.read().unwrap().get("theme");        // shared: many readers at once
settings.write().unwrap().insert(k, v);       // exclusive: waits until no one reads
```

(A fragment.) It is worth it when reads vastly outnumber writes, as with
configuration. When reads and writes are about equal, or locks are held only
briefly, a `Mutex` is simpler and often just as fast.

## Atomics: lock-free counters and flags

For a single integer or `bool`, a whole lock is more than needed. The
**atomic** types in `std::sync::atomic` (`AtomicU64`, `AtomicUsize`,
`AtomicBool`, ...) are numbers whose operations the processor performs as
one indivisible step, without any lock:

```rust
use std::sync::atomic::{AtomicU64, Ordering};

static REQUESTS: AtomicU64 = AtomicU64::new(0);
REQUESTS.fetch_add(1, Ordering::Relaxed);     // add 1, as one indivisible step
REQUESTS.load(Ordering::Relaxed)              // read the current value
```

(A fragment.) Note that `fetch_add` takes `&self`: atomics can be changed
through a shared reference, which is why one can live in a `static` (a
global variable) or an `Arc` and be updated from every thread.

A plain `counter += 1` is really three steps: read, add, write back. Two
threads can both read 5 and both write 6, losing one count. `fetch_add` does
the three steps as one.

`Ordering` here has nothing to do with sorting. It controls how this
operation is ordered relative to *other* memory operations around it, as
seen from other threads. `Relaxed`, the weakest, only guarantees the
operation itself is atomic, which is all a statistics counter needs. The
Pro track's atomics lesson explains the stronger orderings and when they
matter.

## Deadlocks

Locks bring a new way to fail. Thread A locks account `x`, then waits to
lock `y`. At the same moment, thread B has locked `y` and waits for `x`.
Each waits for the other, forever: a **deadlock**.

```text
 thread A:  holds x ─── wants y ───┐
                                   │   both wait forever
 thread B:  holds y ─── wants x ───┘
```

That is exactly what happens to a `transfer(from, to)` that always locks
`from` first, the moment two threads transfer in opposite directions.

The standard cure is a **global lock order**: whenever code needs more than
one lock, it always takes them in the same order, for example by an id
number. Then both threads try `x` first (say it has the lower id), one of
them gets it, and the other waits *before* holding anything, so the cycle
cannot form.

Rust prevents data races at compile time, but **not** deadlocks or the race
condition above: those are about the logic of your program, which the
compiler cannot see. (One more consequence: locking the same `Mutex` twice
in one thread also deadlocks, or panics, since the second `lock()` waits for
a lock that thread itself holds. So `transfer` from an account to itself
must not lock both.)

## Run it

```rust
use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, RwLock};
use std::thread;

static REQUESTS: AtomicU64 = AtomicU64::new(0);

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let handles: Vec<_> = (0..8)
        .map(|_| {
            let counter = Arc::clone(&counter);
            thread::spawn(move || {
                for _ in 0..1000 {
                    *counter.lock().unwrap() += 1;
                    REQUESTS.fetch_add(1, Ordering::Relaxed);
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    println!("{} {}", *counter.lock().unwrap(), REQUESTS.load(Ordering::Relaxed));
    println!("{}", Arc::strong_count(&counter));    // the threads' clones are gone

    let settings = RwLock::new(HashMap::new());
    settings.write().unwrap().insert("theme", "dark");
    let r1 = settings.read().unwrap();
    let r2 = settings.read().unwrap();              // two readers at once
    println!("{:?} {}", r1.get("theme"), r2.len());
    drop((r1, r2));

    let m = Arc::new(Mutex::new(0));
    let m2 = Arc::clone(&m);
    let _ = thread::spawn(move || {
        let _guard = m2.lock().unwrap();
        panic!("while holding the lock");
    })
    .join();
    println!("{}", m.lock().is_err());              // poisoned
}
```

```output
8000 8000
1
Some("dark") 1
true
```

8 threads × 1000 increments came to exactly 8000 both ways: through the
mutex and through the atomic. Once the threads finished, their `Arc`
clones were dropped, leaving 1. The two read guards existed at the same
time without blocking each other; `drop((r1, r2))` released both. The last
thread panicked while holding `m`'s lock, so `m` is poisoned. (Its panic
message goes to standard error, so it is not shown above.)

## Your turn

In `src/lib.rs`:

- `BankAccount`: a cloneable handle to one shared account; every clone sees
  the same balance (the tests deposit from 8 threads at once)
  - `new(id, balance)`, `deposit(&self, amount)`, `balance(&self)`
  - `withdraw(&self, amount) -> bool`: takes the money and returns `true`,
    or, if the balance is less than `amount`, returns `false` and changes
    nothing. Check and subtract under **one** lock: the tests make 2000
    withdrawals of 1 from 10 threads against a balance of 1000, and require
    exactly 1000 to succeed.
- `transfer(from, to, amount) -> bool`: moves `amount` from `from` to `to`,
  or returns `false` and changes nothing if `from` has too little. Hold both
  locks for the whole check-and-move, so no one sees the money in neither
  account or both. It must **not deadlock** when two threads transfer between
  the same two accounts in opposite directions (the tests do 20,000 each way):
  lock the account with the smaller `id` first.
- `HitCounter`: cloneable, all clones counting together, with `hit()` and
  `total()`, lock-free: the tests check your source mentions `AtomicU64`
- `ConfigStore`: cloneable, backed by an `RwLock`, with
  `get(&self, key) -> Option<String>` (a copy of the value) and
  `set(&self, key, value)`
