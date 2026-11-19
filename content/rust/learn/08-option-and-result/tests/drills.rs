#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_half_if_even() {
    assert_eq!(half_if_even(8), Some(4));
    assert_eq!(half_if_even(7), None);
}

#[test]
fn drill_02_or_zero() {
    assert_eq!(or_zero(Some(5)), 5);
    assert_eq!(or_zero(None), 0);
}

#[test]
fn drill_03_doubled() {
    assert_eq!(doubled(Some(3)), Some(6));
    assert_eq!(doubled(None), None);
}

#[test]
fn drill_04_has_value() {
    assert!(has_value(Some(1)));
    assert!(!has_value(None));
}

#[test]
fn drill_05_parse_opt() {
    assert_eq!(parse_opt(" 12 "), Some(12));
    assert_eq!(parse_opt("x"), None);
}

#[test]
fn drill_06_parse_or_zero() {
    assert_eq!(parse_or_zero("7"), 7);
    assert_eq!(parse_or_zero("seven"), 0);
}

#[test]
fn drill_07_parse_message() {
    assert_eq!(parse_message("5"), Ok(5));
    assert_eq!(parse_message("x"), Err("invalid digit found in string".to_string()));
}

#[test]
fn drill_08_check_age() {
    assert_eq!(check_age(30), Ok(30));
    assert_eq!(check_age(200), Err("bad age: 200".to_string()));
}

#[test]
fn drill_09_double_text() {
    assert_eq!(double_text("21"), Ok(42));
    assert!(double_text("x").is_err());
}

#[test]
fn drill_10_position_of() {
    assert_eq!(position_of(&[5, 7, 9], 9), Some(2));
    assert_eq!(position_of(&[5, 7], 1), None);
}
