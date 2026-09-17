use std::collections::HashSet;
use std::sync::Arc;
use std::thread;

use atomics_lesson::*;

#[test]
fn counter_under_contention() {
    let c = Arc::new(Counter::new());
    thread::scope(|s| {
        for _ in 0..8 {
            let c = Arc::clone(&c);
            s.spawn(move || {
                for _ in 0..50_000 {
                    c.increment();
                }
            });
        }
    });
    assert_eq!(c.get(), 400_000);
    c.add(100);
    assert_eq!(c.reset(), 400_100);
    assert_eq!(c.get(), 0);
}

#[test]
fn flag_publishes_data() {
    let flag = Arc::new(Flag::new());
    let data = Arc::new(SpinLock::new(Vec::new()));
    assert!(!flag.is_set());

    let (f, d) = (Arc::clone(&flag), Arc::clone(&data));
    let writer = thread::spawn(move || {
        d.lock().push(42);
        f.set();
    });
    writer.join().unwrap();

    assert!(flag.is_set());
    assert_eq!(*data.lock(), [42]);
}

#[test]
fn ids_are_unique_and_bounded() {
    let ids = Arc::new(IdGenerator::new(0, 10_000));
    let mut all = Vec::new();
    thread::scope(|s| {
        let handles: Vec<_> = (0..8).map(|_| s.spawn(|| std::iter::from_fn(|| ids.next_id()).collect::<Vec<_>>())).collect();
        for h in handles {
            all.extend(h.join().unwrap());
        }
    });
    assert_eq!(all.len(), 10_000);
    assert_eq!(all.iter().copied().collect::<HashSet<_>>().len(), 10_000);
    assert_eq!(ids.next_id(), None);
}

#[test]
fn id_generator_range() {
    let ids = IdGenerator::new(100, 103);
    assert_eq!((ids.next_id(), ids.next_id(), ids.next_id(), ids.next_id()), (Some(100), Some(101), Some(102), None));
    assert_eq!(IdGenerator::new(5, 5).next_id(), None);
}

#[test]
fn spin_lock_guards_the_value() {
    let lock = Arc::new(SpinLock::new(0u64));
    thread::scope(|s| {
        for _ in 0..4 {
            let lock = Arc::clone(&lock);
            s.spawn(move || {
                for _ in 0..20_000 {
                    let mut guard = lock.lock();
                    *guard += 1;
                }
            });
        }
    });
    assert_eq!(*lock.lock(), 80_000);
}

#[test]
fn orderings_are_deliberate() {
    let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    assert!(src.contains("Ordering::Release"), "Flag::set should publish with Release");
    assert!(src.contains("Ordering::Acquire"), "Flag::is_set should observe with Acquire");
    assert!(src.contains("compare_exchange"), "IdGenerator needs a compare-and-swap loop");
}
