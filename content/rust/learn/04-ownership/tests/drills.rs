#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_make_greeting() {
    assert_eq!(make_greeting(), "hello");
}

#[test]
fn drill_02_add_question_mark() {
    assert_eq!(add_question_mark("why".to_string()), "why?");
}

#[test]
fn drill_03_copy_of() {
    let s = "keep".to_string();
    assert_eq!(copy_of(&s), "keep");
    assert_eq!(s, "keep");
}

#[test]
fn drill_04_first_copy() {
    let names = vec!["ana".to_string(), "bo".to_string()];
    assert_eq!(first_copy(&names), "ana");
    assert_eq!(names.len(), 2);
}

#[test]
fn drill_05_take_first() {
    assert_eq!(take_first(vec!["ana".to_string(), "bo".to_string()]), "ana");
}

#[test]
fn drill_06_total_length() {
    let words = vec!["ab".to_string(), "cde".to_string()];
    assert_eq!(total_length(&words), 5);
}

#[test]
fn drill_07_count_then_keep() {
    let (n, words) = count_then_keep(vec!["x".to_string(), "y".to_string()]);
    assert_eq!(n, 2);
    assert_eq!(words, vec!["x", "y"]);
}

#[test]
fn drill_08_both_ways() {
    assert_eq!(both_ways("hi".to_string()), ("hi".to_string(), "hi".to_string()));
}
