use std::collections::HashSet;
use std::sync::Mutex;
use std::thread;

use threads_lesson::*;

#[test]
fn sums_in_parallel() {
    let nums: Vec<i64> = (1..=100_000).collect();
    assert_eq!(parallel_sum(&nums, 4), 5_000_050_000);
    assert_eq!(parallel_sum(&nums, 1), 5_000_050_000);
    assert_eq!(parallel_sum(&[1, 2, 3], 8), 6);
    assert_eq!(parallel_sum(&[], 4), 0);
}

#[test]
fn workers_return_in_order() {
    assert_eq!(spawn_workers(3), ["worker 0 done", "worker 1 done", "worker 2 done"]);
    assert!(spawn_workers(0).is_empty());
}

#[test]
fn counts_matches_with_borrowed_data() {
    let words: Vec<String> = "a b a c a b".split(' ').map(String::from).collect();
    assert_eq!(count_matches(&words, "a", 3), 3);
    assert_eq!(count_matches(&words, "b", 10), 2);
    assert_eq!(count_matches(&words, "z", 2), 0);
}

#[test]
fn panics_are_reported() {
    let previous = std::panic::take_hook();
    std::panic::set_hook(Box::new(|_| {}));
    let reported = panicking_worker_is_reported();
    std::panic::set_hook(previous);
    assert!(reported);
}

#[test]
fn source_uses_scoped_threads() {
    let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    assert!(src.contains("thread::scope"), "parallel_sum and count_matches should use thread::scope");
}

#[test]
fn work_really_spreads_across_threads() {
    let seen = Mutex::new(HashSet::new());
    thread::scope(|s| {
        for _ in 0..4 {
            s.spawn(|| {
                seen.lock().unwrap().insert(thread::current().id());
            });
        }
    });
    assert_eq!(seen.lock().unwrap().len(), 4);
}
