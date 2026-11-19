// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, then press that drill's Run button in the
// Results tab: it builds and tests just that drill, so a mistake in one never
// stops the others. Keep the `/// Drill N:` lines; they mark where each drill
// starts. The hidden tests read this file directly, so it needs no `mod` line.

/// Drill 1: `call_twice(|x| x + 3, 1)` is `7`
pub fn call_twice<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 {
    f(f(x))
}

/// Drill 2: `doubled(&[1, 2, 3])` is `vec![2, 4, 6]`
pub fn doubled(nums: &[i32]) -> Vec<i32> {
    nums.iter().map(|n| n * 2).collect()
}

/// Drill 3: `positives(&[3, -1, 0, 5])` is `vec![3, 5]`
pub fn positives(nums: &[i32]) -> Vec<i32> {
    nums.iter().filter(|n| **n > 0).copied().collect()
}

/// Drill 4: `count_odd(&[1, 2, 3])` is `2`
pub fn count_odd(nums: &[i32]) -> usize {
    nums.iter().filter(|n| *n % 2 != 0).count()
}

/// Drill 5: `product(&[2, 3, 4])` is `24`; an empty slice gives `1`
pub fn product(nums: &[i32]) -> i32 {
    nums.iter().fold(1, |acc, n| acc * n)
}

/// Drill 6: `sum_of_squares(&[1, 2, 3])` is `14`
pub fn sum_of_squares(nums: &[i32]) -> i32 {
    nums.iter().map(|n| n * n).sum()
}

/// Drill 7: `word_lengths("a bb  ccc")` is `vec![1, 2, 3]`
pub fn word_lengths(text: &str) -> Vec<usize> {
    text.split_whitespace().map(|w| w.len()).collect()
}

/// Drill 8: `vowels("banana")` is `3`
pub fn vowels(s: &str) -> usize {
    s.chars().filter(|c| matches!(c, 'a' | 'e' | 'i' | 'o' | 'u')).count()
}

/// Drill 9: `multiplier(3)` is a closure: `multiplier(3)(5)` is `15`
pub fn multiplier(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x * n
}
