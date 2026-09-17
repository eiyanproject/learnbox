use std::cell::UnsafeCell;
use std::ops::{Deref, DerefMut};
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};

#[derive(Default)]
pub struct Counter {
    value: AtomicUsize,
}

impl Counter {
    pub fn new() -> Self {
        Counter { value: AtomicUsize::new(0) }
    }

    // increment, add, get, reset
}

#[derive(Default)]
pub struct Flag {
    raised: AtomicBool,
}

impl Flag {
    pub fn new() -> Self {
        Flag { raised: AtomicBool::new(false) }
    }

    // set, is_set
}

pub struct IdGenerator {
    next: AtomicU64,
    max: u64,
}

impl IdGenerator {
    pub fn new(start: u64, max: u64) -> Self {
        IdGenerator { next: AtomicU64::new(start), max }
    }

    pub fn next_id(&self) -> Option<u64> {
        todo!()
    }
}

pub struct SpinLock<T> {
    locked: AtomicBool,
    value: UnsafeCell<T>,
}

// SAFETY: the lock gives exclusive access to the value, so it is safe to share
// a SpinLock between threads as long as T can be sent to another thread.
unsafe impl<T: Send> Sync for SpinLock<T> {}

impl<T> SpinLock<T> {
    pub fn new(value: T) -> Self {
        SpinLock { locked: AtomicBool::new(false), value: UnsafeCell::new(value) }
    }

    // lock() -> SpinGuard<'_, T>
}
