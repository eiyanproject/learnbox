#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_one_two_three() {
    assert_eq!(one_two_three(), vec![1, 2, 3]);
}

#[test]
fn drill_02_with_extra() {
    assert_eq!(with_extra(vec![1], 2), vec![1, 2]);
}

#[test]
fn drill_03_last_out() {
    assert_eq!(last_out(vec![1, 2]), Some(2));
    assert_eq!(last_out(vec![]), None);
}

#[test]
fn drill_04_safe_get() {
    assert_eq!(safe_get(&[10, 20], 1), Some(&20));
    assert_eq!(safe_get(&[10, 20], 5), None);
}

#[test]
fn drill_05_sorted() {
    assert_eq!(sorted(vec![3, 1, 2]), vec![1, 2, 3]);
}

#[test]
fn drill_06_words() {
    assert_eq!(words(" a  b "), vec!["a", "b"]);
}

#[test]
fn drill_07_join_words() {
    assert_eq!(join_words(&["a", "b"]), "a b");
}

#[test]
fn drill_08_quiet() {
    assert_eq!(quiet("HeLLo"), "hello");
}

#[test]
fn drill_09_ages() {
    let m = ages();
    assert_eq!(m.len(), 2);
    assert_eq!(m["ana"], 30);
    assert_eq!(m["bo"], 25);
}

#[test]
fn drill_10_letter_counts() {
    let m = letter_counts("aab");
    assert_eq!(m.len(), 2);
    assert_eq!(m[&'a'], 2);
    assert_eq!(m[&'b'], 1);
}
