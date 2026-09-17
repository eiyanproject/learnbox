use std::collections::HashSet;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use channels_lesson::*;

#[test]
fn producers() {
    let all = collect_from_producers(3, 2);
    assert_eq!(all, ["p0-0", "p0-1", "p1-0", "p1-1", "p2-0", "p2-1"]);
    assert!(collect_from_producers(0, 5).is_empty());
}

#[test]
fn many_producers_finish() {
    assert_eq!(collect_from_producers(8, 500).len(), 4000);
}

#[test]
fn pool_runs_every_job_before_shutdown_returns() {
    let pool = WorkerPool::new(4);
    let done = Arc::new(AtomicUsize::new(0));
    for _ in 0..100 {
        let done = Arc::clone(&done);
        pool.execute(move || {
            thread::sleep(Duration::from_millis(1));
            done.fetch_add(1, Ordering::SeqCst);
        });
    }
    pool.shutdown();
    assert_eq!(done.load(Ordering::SeqCst), 100);
}

#[test]
fn pool_runs_jobs_concurrently() {
    let pool = WorkerPool::new(4);
    let threads = Arc::new(Mutex::new(HashSet::new()));
    let start = Instant::now();
    for _ in 0..8 {
        let threads = Arc::clone(&threads);
        pool.execute(move || {
            threads.lock().unwrap().insert(thread::current().id());
            thread::sleep(Duration::from_millis(100));
        });
    }
    pool.shutdown();
    assert!(start.elapsed() < Duration::from_millis(600), "jobs ran one at a time");
    assert!(threads.lock().unwrap().len() >= 2);
}

#[test]
#[should_panic]
fn pool_needs_a_worker() {
    WorkerPool::new(0);
}

#[test]
fn pipeline_stages() {
    assert_eq!(pipeline(5), [1, 4, 9, 16, 25]);
    assert!(pipeline(0).is_empty());
    assert_eq!(pipeline(10_000).len(), 10_000);
}
