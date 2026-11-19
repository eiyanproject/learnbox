#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_plus_one() {
    assert_eq!(plus_one(4), 5);
    assert_eq!(plus_one(-1), 0);
}

#[test]
fn drill_02_area() {
    assert_eq!(area(3, 4), 12);
    assert_eq!(area(5, 1), 5);
}

#[test]
fn drill_03_hello() {
    assert_eq!(hello(), "hello");
}

#[test]
fn drill_04_shout() {
    assert_eq!(shout("hi"), "hi!");
    assert_eq!(shout("rust"), "rust!");
}

#[test]
fn drill_05_full_name() {
    assert_eq!(full_name("Ada", "Lovelace"), "Ada Lovelace");
}

#[test]
fn drill_06_score_line() {
    assert_eq!(score_line("Ana", 92), "Ana:    92");
    assert_eq!(score_line("Bo", 12345), "Bo: 12345");
}

#[test]
fn drill_07_letters() {
    assert_eq!(letters("cargo"), 5);
    assert_eq!(letters(""), 0);
}

#[test]
fn drill_08_stars() {
    assert_eq!(stars(3), "***");
    assert_eq!(stars(0), "");
}

#[test]
fn drill_09_two_lines() {
    assert_eq!(two_lines("a", "b"), "a\nb");
}

#[test]
fn drill_10_underline() {
    assert_eq!(underline("hi"), "hi\n--");
    assert_eq!(underline("cargo"), "cargo\n-----");
}
