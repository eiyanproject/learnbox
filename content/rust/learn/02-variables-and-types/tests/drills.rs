#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_to_float() {
    assert_eq!(to_float(3), 3.0);
    assert_eq!(to_float(-2), -2.0);
}

#[test]
fn drill_02_whole_part() {
    assert_eq!(whole_part(3.9), 3);
    assert_eq!(whole_part(7.0), 7);
}

#[test]
fn drill_03_half() {
    assert_eq!(half(5.0), 2.5);
}

#[test]
fn drill_04_plus_ten() {
    assert_eq!(plus_ten(5), 15);
}

#[test]
fn drill_05_swap() {
    assert_eq!(swap((1, 2)), (2, 1));
}

#[test]
fn drill_06_minutes_and_seconds() {
    assert_eq!(minutes_and_seconds(125), (2, 5));
    assert_eq!(minutes_and_seconds(59), (0, 59));
}

#[test]
fn drill_07_first() {
    assert_eq!(first([7, 8, 9]), 7);
}

#[test]
fn drill_08_zeros() {
    assert_eq!(zeros(), [0, 0, 0, 0]);
}

#[test]
fn drill_09_parse_number() {
    assert_eq!(parse_number("42"), 42);
    assert_eq!(parse_number("-7"), -7);
}

#[test]
fn drill_10_biggest_u8() {
    assert_eq!(biggest_u8(), 255);
}
