#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_call_twice() {
    assert_eq!(call_twice(|x| x + 3, 1), 7);
    assert_eq!(call_twice(|x| x * x, 3), 81);
}

#[test]
fn drill_02_doubled() {
    assert_eq!(doubled(&[1, 2, 3]), vec![2, 4, 6]);
}

#[test]
fn drill_03_positives() {
    assert_eq!(positives(&[3, -1, 0, 5]), vec![3, 5]);
}

#[test]
fn drill_04_count_odd() {
    assert_eq!(count_odd(&[1, 2, 3]), 2);
    assert_eq!(count_odd(&[-3]), 1);
}

#[test]
fn drill_05_product() {
    assert_eq!(product(&[2, 3, 4]), 24);
    assert_eq!(product(&[]), 1);
}

#[test]
fn drill_06_sum_of_squares() {
    assert_eq!(sum_of_squares(&[1, 2, 3]), 14);
}

#[test]
fn drill_07_word_lengths() {
    assert_eq!(word_lengths("a bb  ccc"), vec![1, 2, 3]);
}

#[test]
fn drill_08_vowels() {
    assert_eq!(vowels("banana"), 3);
    assert_eq!(vowels("xyz"), 0);
}

#[test]
fn drill_09_multiplier() {
    let times3 = multiplier(3);
    assert_eq!(times3(5), 15);
    assert_eq!(times3(0), 0);
}
