// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, then press that drill's Run button in the
// Results tab: it builds and tests just that drill, so a mistake in one never
// stops the others. Keep the `/// Drill N:` lines; they mark where each drill
// starts. The hidden tests read this file directly, so it needs no `mod` line.

use std::num::ParseIntError;

/// Drill 1: `half_if_even(8)` is `Some(4)`; an odd number gives `None`
pub fn half_if_even(n: i32) -> Option<i32> {
    todo!()
}

/// Drill 2: `or_zero(Some(5))` is `5`, `or_zero(None)` is `0`
pub fn or_zero(opt: Option<i32>) -> i32 {
    todo!()
}

/// Drill 3: `doubled(Some(3))` is `Some(6)`, `doubled(None)` is `None`
pub fn doubled(opt: Option<i32>) -> Option<i32> {
    todo!()
}

/// Drill 4: `has_value(Some(1))` is `true`
pub fn has_value(opt: Option<i32>) -> bool {
    todo!()
}

/// Drill 5: `parse_opt(" 12 ")` is `Some(12)`, `parse_opt("x")` is `None`
pub fn parse_opt(s: &str) -> Option<i32> {
    todo!()
}

/// Drill 6: `parse_or_zero("7")` is `7`, `parse_or_zero("seven")` is `0`
pub fn parse_or_zero(s: &str) -> i32 {
    todo!()
}

/// Drill 7: `parse_message("x")` is `Err("invalid digit found in string")`; `"5"` is `Ok(5)`
pub fn parse_message(s: &str) -> Result<i32, String> {
    todo!()
}

/// Drill 8: `check_age(30)` is `Ok(30)`; outside 0 to 150 is `Err("bad age: 200")`
pub fn check_age(n: i32) -> Result<i32, String> {
    todo!()
}

/// Drill 9: `double_text("21")` is `Ok(42)`; bad text passes the parse error up
pub fn double_text(s: &str) -> Result<i32, ParseIntError> {
    todo!()
}

/// Drill 10: `position_of(&[5, 7, 9], 9)` is `Some(2)`
pub fn position_of(items: &[i32], target: i32) -> Option<usize> {
    todo!()
}
