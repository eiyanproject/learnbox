// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, press Check, and that drill gets its own
// tick in the Results tab. The hidden tests read this file directly, so it
// needs no `mod` line anywhere.

use std::collections::HashMap;

/// Drill 1: `one_two_three()` is `vec![1, 2, 3]`
pub fn one_two_three() -> Vec<i32> {
    todo!()
}

/// Drill 2: `with_extra(vec![1], 2)` is `vec![1, 2]`
pub fn with_extra(mut v: Vec<i32>, x: i32) -> Vec<i32> {
    todo!()
}

/// Drill 3: `last_out(vec![1, 2])` is `Some(2)`; an empty vector gives `None`
pub fn last_out(mut v: Vec<i32>) -> Option<i32> {
    todo!()
}

/// Drill 4: `safe_get(&[10, 20], 1)` is `Some(&20)`; past the end is `None`
pub fn safe_get(v: &[i32], i: usize) -> Option<&i32> {
    todo!()
}

/// Drill 5: `sorted(vec![3, 1, 2])` is `vec![1, 2, 3]`
pub fn sorted(mut v: Vec<i32>) -> Vec<i32> {
    todo!()
}

/// Drill 6: `words(" a  b ")` is `vec!["a", "b"]`
pub fn words(text: &str) -> Vec<&str> {
    todo!()
}

/// Drill 7: `join_words(&["a", "b"])` is `"a b"`
pub fn join_words(words: &[&str]) -> String {
    todo!()
}

/// Drill 8: `quiet("HeLLo")` is `"hello"`
pub fn quiet(s: &str) -> String {
    todo!()
}

/// Drill 9: `ages()` is a map with `"ana"` → `30` and `"bo"` → `25`
pub fn ages() -> HashMap<String, u32> {
    todo!()
}

/// Drill 10: `letter_counts("aab")` maps `'a'` → `2` and `'b'` → `1`
pub fn letter_counts(text: &str) -> HashMap<char, usize> {
    todo!()
}
