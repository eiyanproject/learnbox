use std::thread;

pub fn parallel_sum(nums: &[i64], threads: usize) -> i64 {
    let chunk_size = nums.len().div_ceil(threads.max(1)).max(1);
    thread::scope(|s| {
        let handles: Vec<_> = nums.chunks(chunk_size).map(|chunk| s.spawn(move || chunk.iter().sum::<i64>())).collect();
        handles.into_iter().map(|h| h.join().unwrap()).sum()
    })
}

pub fn spawn_workers(n: usize) -> Vec<String> {
    let handles: Vec<_> = (0..n).map(|i| thread::spawn(move || format!("worker {i} done"))).collect();
    handles.into_iter().map(|h| h.join().unwrap()).collect()
}

pub fn count_matches(words: &[String], needle: &str, threads: usize) -> usize {
    let chunk_size = words.len().div_ceil(threads.max(1)).max(1);
    thread::scope(|s| {
        let handles: Vec<_> = words
            .chunks(chunk_size)
            .map(|chunk| s.spawn(move || chunk.iter().filter(|w| w.as_str() == needle).count()))
            .collect();
        handles.into_iter().map(|h| h.join().unwrap()).sum()
    })
}

pub fn panicking_worker_is_reported() -> bool {
    let handle = thread::spawn(|| {
        panic!("worker failed");
    });
    handle.join().is_err()
}
