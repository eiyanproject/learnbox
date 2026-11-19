#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_sign() {
    assert_eq!(sign(-4), "negative");
    assert_eq!(sign(0), "zero");
    assert_eq!(sign(9), "positive");
}

#[test]
fn drill_02_is_even() {
    assert!(is_even(6));
    assert!(!is_even(7));
}

#[test]
fn drill_03_sum_to() {
    assert_eq!(sum_to(4), 10);
    assert_eq!(sum_to(0), 0);
}

#[test]
fn drill_04_count_down() {
    assert_eq!(count_down(3), vec![3, 2, 1]);
}

#[test]
fn drill_05_evens_below() {
    assert_eq!(evens_below(7), vec![0, 2, 4, 6]);
}

#[test]
fn drill_06_halvings() {
    assert_eq!(halvings(8), 3);
    assert_eq!(halvings(1), 0);
    assert_eq!(halvings(10), 3);
}

#[test]
fn drill_07_next_multiple_of_7() {
    assert_eq!(next_multiple_of_7(10), 14);
    assert_eq!(next_multiple_of_7(21), 21);
}

#[test]
fn drill_08_number_text() {
    assert_eq!(number_text(42), "42");
}

#[test]
fn drill_09_fizz() {
    assert_eq!(fizz(9), "Fizz");
    assert_eq!(fizz(4), "4");
}
