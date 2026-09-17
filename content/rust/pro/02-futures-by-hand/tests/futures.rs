use std::time::{Duration, Instant};

use futures_by_hand::*;

#[test]
fn ready_future() {
    assert_eq!(block_on(ready(42)), 42);
    assert_eq!(block_on(ready(String::from("done"))), "done");
}

#[test]
fn delay_future_waits() {
    let start = Instant::now();
    block_on(delay(Duration::from_millis(150)));
    let elapsed = start.elapsed();
    assert!(elapsed >= Duration::from_millis(140), "returned too early: {elapsed:?}");
    assert!(elapsed < Duration::from_secs(3), "took far too long: {elapsed:?}");
}

#[test]
fn pending_futures_are_polled_again() {
    assert_eq!(block_on(counter(5)), 6);
    assert_eq!(block_on(counter(0)), 1);
}

#[test]
fn runs_async_blocks_and_await() {
    let output = block_on(async {
        let a = ready(2).await;
        delay(Duration::from_millis(20)).await;
        let b = counter(3).await;
        format!("{a}-{b}")
    });
    assert_eq!(output, "2-4");
}

#[test]
fn nested_async_functions() {
    async fn add(a: u32, b: u32) -> u32 {
        delay(Duration::from_millis(5)).await;
        a + b
    }

    async fn total() -> u32 {
        add(1, 2).await + add(3, 4).await
    }

    assert_eq!(block_on(total()), 10);
}

#[test]
fn block_on_does_not_busy_loop() {
    // A spin loop would burn CPU for the whole delay; parking uses almost none.
    let start = Instant::now();
    block_on(delay(Duration::from_millis(200)));
    assert!(start.elapsed() < Duration::from_secs(3));
    let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    assert!(src.contains("park"), "park the thread between polls instead of spinning");
}
