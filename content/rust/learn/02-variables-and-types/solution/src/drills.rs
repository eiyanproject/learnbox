// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, press Check, and that drill gets its own
// tick in the Results tab. The hidden tests read this file directly, so it
// needs no `mod` line anywhere.

/// Drill 1: `to_float(3)` is `3.0`
pub fn to_float(n: i32) -> f64 {
    n as f64
}

/// Drill 2: `whole_part(3.9)` is `3`
pub fn whole_part(x: f64) -> i32 {
    x as i32
}

/// Drill 3: `half(5.0)` is `2.5`
pub fn half(x: f64) -> f64 {
    x / 2.0
}

/// Drill 4: `plus_ten(5)` is `15`, using a `let mut` variable and `+=`
pub fn plus_ten(n: i32) -> i32 {
    let mut total = n;
    total += 10;
    total
}

/// Drill 5: `swap((1, 2))` is `(2, 1)`
pub fn swap(pair: (i32, i32)) -> (i32, i32) {
    (pair.1, pair.0)
}

/// Drill 6: `minutes_and_seconds(125)` is `(2, 5)`
pub fn minutes_and_seconds(total: u32) -> (u32, u32) {
    (total / 60, total % 60)
}

/// Drill 7: `first([7, 8, 9])` is `7`
pub fn first(values: [i32; 3]) -> i32 {
    values[0]
}

/// Drill 8: `zeros()` is `[0, 0, 0, 0]`
pub fn zeros() -> [i32; 4] {
    [0; 4]
}

/// Drill 9: `parse_number("42")` is `42`
pub fn parse_number(text: &str) -> i32 {
    text.parse().unwrap()
}

/// Drill 10: `biggest_u8()` is `255`, the largest `u8`
pub fn biggest_u8() -> u8 {
    u8::MAX
}
