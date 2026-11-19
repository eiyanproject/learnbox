// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, then press that drill's Run button in the
// Results tab: it builds and tests just that drill, so a mistake in one never
// stops the others. Keep the `/// Drill N:` lines; they mark where each drill
// starts. The hidden tests read this file directly, so it needs no `mod` line.

use std::collections::HashMap;

/// Drill 1: `one_two_three()` is `vec![1, 2, 3]`
pub fn one_two_three() -> Vec<i32> {
    vec![1, 2, 3]
}

/// Drill 2: `with_extra(vec![1], 2)` is `vec![1, 2]`
pub fn with_extra(mut v: Vec<i32>, x: i32) -> Vec<i32> {
    v.push(x);
    v
}

/// Drill 3: `last_out(vec![1, 2])` is `Some(2)`; an empty vector gives `None`
pub fn last_out(mut v: Vec<i32>) -> Option<i32> {
    v.pop()
}

/// Drill 4: `safe_get(&[10, 20], 1)` is `Some(&20)`; past the end is `None`
pub fn safe_get(v: &[i32], i: usize) -> Option<&i32> {
    v.get(i)
}

/// Drill 5: `sorted(vec![3, 1, 2])` is `vec![1, 2, 3]`
pub fn sorted(mut v: Vec<i32>) -> Vec<i32> {
    v.sort();
    v
}

/// Drill 6: `words(" a  b ")` is `vec!["a", "b"]`
pub fn words(text: &str) -> Vec<&str> {
    text.split_whitespace().collect()
}

/// Drill 7: `join_words(&["a", "b"])` is `"a b"`
pub fn join_words(words: &[&str]) -> String {
    words.join(" ")
}

/// Drill 8: `quiet("HeLLo")` is `"hello"`
pub fn quiet(s: &str) -> String {
    s.to_lowercase()
}

/// Drill 9: `ages()` is a map with `"ana"` → `30` and `"bo"` → `25`
pub fn ages() -> HashMap<String, u32> {
    let mut map = HashMap::new();
    map.insert("ana".to_string(), 30);
    map.insert("bo".to_string(), 25);
    map
}

/// Drill 10: `letter_counts("aab")` maps `'a'` → `2` and `'b'` → `1`
pub fn letter_counts(text: &str) -> HashMap<char, usize> {
    let mut counts = HashMap::new();
    for c in text.chars() {
        *counts.entry(c).or_insert(0) += 1;
    }
    counts
}
