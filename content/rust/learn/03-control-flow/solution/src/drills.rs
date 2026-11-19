// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, press Check, and that drill gets its own
// tick in the Results tab. The hidden tests read this file directly, so it
// needs no `mod` line anywhere.

/// Drill 1: `sign(-4)` is `"negative"`; also `"zero"` and `"positive"`
pub fn sign(n: i32) -> String {
    if n < 0 {
        "negative".to_string()
    } else if n == 0 {
        "zero".to_string()
    } else {
        "positive".to_string()
    }
}

/// Drill 2: `is_even(6)` is `true`
pub fn is_even(n: u32) -> bool {
    n % 2 == 0
}

/// Drill 3: `sum_to(4)` is `10`: 1 + 2 + 3 + 4
pub fn sum_to(n: u32) -> u32 {
    let mut total = 0;
    for i in 1..=n {
        total += i;
    }
    total
}

/// Drill 4: `count_down(3)` is `vec![3, 2, 1]`
pub fn count_down(n: u32) -> Vec<u32> {
    (1..=n).rev().collect()
}

/// Drill 5: `evens_below(7)` is `vec![0, 2, 4, 6]`
pub fn evens_below(n: u32) -> Vec<u32> {
    (0..n).step_by(2).collect()
}

/// Drill 6: `halvings(8)` is `3`: how many halvings to get from `n` down to 1
pub fn halvings(n: u32) -> u32 {
    let mut n = n;
    let mut count = 0;
    while n > 1 {
        n /= 2;
        count += 1;
    }
    count
}

/// Drill 7: `next_multiple_of_7(10)` is `14`: the first multiple of 7 at or after `start`
pub fn next_multiple_of_7(start: u32) -> u32 {
    let mut n = start;
    loop {
        if n % 7 == 0 {
            break n;
        }
        n += 1;
    }
}

/// Drill 8: `number_text(42)` is `"42"`
pub fn number_text(n: u32) -> String {
    n.to_string()
}

/// Drill 9: `fizz(9)` is `"Fizz"`, `fizz(4)` is `"4"`
pub fn fizz(n: u32) -> String {
    if n % 3 == 0 {
        "Fizz".to_string()
    } else {
        n.to_string()
    }
}
