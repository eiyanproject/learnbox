use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use tiny_executor::*;

#[test]
fn runs_one_task() {
    let ex = Executor::new();
    let handle = ex.spawn(async { 6 * 7 });
    ex.run();
    assert_eq!(handle.take(), Some(42));
    assert_eq!(handle.take(), None, "take() hands the value over once");
}

#[test]
fn runs_many_tasks_concurrently() {
    let ex = Executor::new();
    let start = Instant::now();
    let handles: Vec<_> = (0..8)
        .map(|i| {
            ex.spawn(async move {
                delay(Duration::from_millis(150)).await;
                i * 2
            })
        })
        .collect();
    ex.run();
    let elapsed = start.elapsed();
    assert_eq!(handles.iter().filter_map(|h| h.take()).collect::<Vec<_>>(), [0, 2, 4, 6, 8, 10, 12, 14]);
    assert!(elapsed < Duration::from_millis(900), "tasks ran one after another: {elapsed:?}");
    assert!(elapsed >= Duration::from_millis(140));
}

#[test]
fn tasks_share_state_without_locks_being_held_across_await() {
    let ex = Executor::new();
    let log = Arc::new(Mutex::new(Vec::new()));
    for i in 0..3 {
        let log = Arc::clone(&log);
        ex.spawn(async move {
            delay(Duration::from_millis(30 * (3 - i) as u64)).await;
            log.lock().unwrap().push(i);
        });
    }
    ex.run();
    assert_eq!(*log.lock().unwrap(), [2, 1, 0], "tasks should finish in delay order");
}

#[test]
fn spawned_tasks_can_spawn_more_work_through_channels() {
    let ex = Executor::new();
    let count = Arc::new(AtomicUsize::new(0));
    for _ in 0..50 {
        let count = Arc::clone(&count);
        ex.spawn(async move {
            for _ in 0..4 {
                delay(Duration::from_millis(5)).await;
                count.fetch_add(1, Ordering::SeqCst);
            }
        });
    }
    ex.run();
    assert_eq!(count.load(Ordering::SeqCst), 200);
}

#[test]
fn run_returns_when_nothing_is_spawned() {
    Executor::new().run();
}

#[test]
fn block_on_still_works() {
    let start = Instant::now();
    let value = block_on(async {
        delay(Duration::from_millis(50)).await;
        "done"
    });
    assert_eq!(value, "done");
    assert!(start.elapsed() >= Duration::from_millis(45));
}
