use std::collections::HashMap;

pub fn word_counts(text: &str) -> HashMap<String, usize> {
    let mut counts = HashMap::new();
    for word in text.split_whitespace() {
        *counts.entry(word.to_lowercase()).or_insert(0) += 1;
    }
    counts
}

pub fn dedup_sorted(mut v: Vec<i32>) -> Vec<i32> {
    v.sort();
    v.dedup();
    v
}

pub fn group_by_length(words: &[&str]) -> HashMap<usize, Vec<String>> {
    let mut groups = HashMap::new();
    for word in words {
        groups.entry(word.len()).or_insert_with(Vec::new).push(word.to_string());
    }
    groups
}

pub fn reverse_words(text: &str) -> String {
    text.split_whitespace().rev().collect::<Vec<_>>().join(" ")
}
