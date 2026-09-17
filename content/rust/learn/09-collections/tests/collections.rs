use std::collections::HashMap;

use vec_string_hashmap::*;

#[test]
fn counts_words_ignoring_case() {
    let counts = word_counts("the cat The hat  THE bat");
    let expected: HashMap<String, usize> =
        [("the", 3), ("cat", 1), ("hat", 1), ("bat", 1)].into_iter().map(|(k, v)| (k.to_string(), v)).collect();
    assert_eq!(counts, expected);
}

#[test]
fn counts_nothing() {
    assert!(word_counts("   ").is_empty());
}

#[test]
fn dedups_and_sorts() {
    assert_eq!(dedup_sorted(vec![3, 1, 3, 2, 1]), vec![1, 2, 3]);
    assert_eq!(dedup_sorted(vec![]), Vec::<i32>::new());
}

#[test]
fn groups_keep_order() {
    let groups = group_by_length(&["ant", "bee", "wasp", "fly", "moth"]);
    assert_eq!(groups.len(), 2);
    assert_eq!(groups[&3], vec!["ant", "bee", "fly"]);
    assert_eq!(groups[&4], vec!["wasp", "moth"]);
}

#[test]
fn reverses_words() {
    assert_eq!(reverse_words("one two  three"), "three two one");
    assert_eq!(reverse_words("solo"), "solo");
    assert_eq!(reverse_words(""), "");
}
