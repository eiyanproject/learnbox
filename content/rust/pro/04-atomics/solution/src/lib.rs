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

    pub fn increment(&self) {
        self.value.fetch_add(1, Ordering::Relaxed);
    }

    pub fn add(&self, n: usize) {
        self.value.fetch_add(n, Ordering::Relaxed);
    }

    pub fn get(&self) -> usize {
        self.value.load(Ordering::Relaxed)
    }

    pub fn reset(&self) -> usize {
        self.value.swap(0, Ordering::Relaxed)
    }
}

#[derive(Default)]
pub struct Flag {
    raised: AtomicBool,
}

impl Flag {
    pub fn new() -> Self {
        Flag { raised: AtomicBool::new(false) }
    }

    /// Release: everything written before this is visible to a thread that
    /// observes the flag with Acquire.
    pub fn set(&self) {
        self.raised.store(true, Ordering::Release);
    }

    pub fn is_set(&self) -> bool {
        self.raised.load(Ordering::Acquire)
    }
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
        let mut current = self.next.load(Ordering::Acquire);
        loop {
            if current >= self.max {
                return None;
            }
            match self.next.compare_exchange_weak(current, current + 1, Ordering::AcqRel, Ordering::Acquire) {
                Ok(_) => return Some(current),
                Err(actual) => current = actual,
            }
        }
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

    pub fn lock(&self) -> SpinGuard<'_, T> {
        while self.locked.compare_exchange_weak(false, true, Ordering::Acquire, Ordering::Relaxed).is_err() {
            std::hint::spin_loop();
        }
        SpinGuard { lock: self }
    }
}

pub struct SpinGuard<'a, T> {
    lock: &'a SpinLock<T>,
}

impl<T> Deref for SpinGuard<'_, T> {
    type Target = T;

    fn deref(&self) -> &T {
        // SAFETY: holding the guard means we own the lock, so no other
        // reference to the value exists.
        unsafe { &*self.lock.value.get() }
    }
}

impl<T> DerefMut for SpinGuard<'_, T> {
    fn deref_mut(&mut self) -> &mut T {
        // SAFETY: as above, and &mut self proves this guard is not shared.
        unsafe { &mut *self.lock.value.get() }
    }
}

impl<T> Drop for SpinGuard<'_, T> {
    fn drop(&mut self) {
        self.lock.locked.store(false, Ordering::Release);
    }
}
