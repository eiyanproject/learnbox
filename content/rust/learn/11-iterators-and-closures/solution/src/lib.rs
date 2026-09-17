pub fn evens_squared(nums: &[i32]) -> Vec<i32> {
    nums.iter().filter(|n| *n % 2 == 0).map(|n| n * n).collect()
}

pub fn count_long_words(text: &str, min_len: usize) -> usize {
    text.split_whitespace().filter(|w| w.len() >= min_len).count()
}

pub fn running_totals(nums: &[i32]) -> Vec<i32> {
    nums.iter()
        .scan(0, |acc, &n| {
            *acc += n;
            Some(*acc)
        })
        .collect()
}

pub fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

pub fn apply_n<F: Fn(i32) -> i32>(f: F, times: usize, x: i32) -> i32 {
    (0..times).fold(x, |acc, _| f(acc))
}
