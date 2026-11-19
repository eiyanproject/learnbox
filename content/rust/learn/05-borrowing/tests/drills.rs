#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_length() {
    let s = "hello".to_string();
    assert_eq!(length(&s), 5);
    assert_eq!(s, "hello");
}

#[test]
fn drill_02_add_one() {
    let mut n = 4;
    add_one(&mut n);
    assert_eq!(n, 5);
}

#[test]
fn drill_03_exclaim() {
    let mut s = "hey".to_string();
    exclaim(&mut s);
    assert_eq!(s, "hey!");
}

#[test]
fn drill_04_first_three() {
    assert_eq!(first_three("rustacean"), "rus");
}

#[test]
fn drill_05_after_first() {
    assert_eq!(after_first("xhello"), "hello");
}

#[test]
fn drill_06_middle() {
    assert_eq!(middle(&[1, 2, 3, 4]), &[2, 3]);
}

#[test]
fn drill_07_char_count() {
    assert_eq!(char_count("héllo"), 5);
    assert_eq!("héllo".len(), 6);
}

#[test]
fn drill_08_space_at() {
    assert_eq!(space_at("hi there"), Some(2));
    assert_eq!(space_at("hi"), None);
}

#[test]
fn drill_09_negate_all() {
    let mut v = [1, -2];
    negate_all(&mut v);
    assert_eq!(v, [-1, 2]);
}

#[test]
fn drill_10_add_line() {
    let mut buf = "a\n".to_string();
    add_line(&mut buf, "b");
    assert_eq!(buf, "a\nb\n");
}
