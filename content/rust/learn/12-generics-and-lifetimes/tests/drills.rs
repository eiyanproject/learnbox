#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_pair_new() {
    assert_eq!(Pair::new(1, 2), Pair { a: 1, b: 2 });
    assert_eq!(Pair::new("x", "y").b, "y");
}

#[test]
fn drill_02_pair_swap() {
    assert_eq!(Pair::new(1, 2).swap(), Pair { a: 2, b: 1 });
}

#[test]
fn drill_03_pair_larger() {
    assert_eq!(Pair::new(3, 9).larger(), 9);
    assert_eq!(Pair::new(2.5, 1.0).larger(), 2.5);
}

#[test]
fn drill_04_wrapper_get() {
    assert_eq!(Wrapper { value: 5 }.get(), &5);
    assert_eq!(Wrapper { value: "hi" }.get(), &"hi");
}

#[test]
fn drill_05_first() {
    assert_eq!(first(&[4, 5]), Some(4));
    assert_eq!(first::<i32>(&[]), None);
    assert_eq!(first(&['a']), Some('a'));
}

#[test]
fn drill_06_shorter() {
    assert_eq!(shorter("hi", "hello"), "hi");
    assert_eq!(shorter("abc", "xy"), "xy");
    assert_eq!(shorter("ab", "cd"), "ab");
}

#[test]
fn drill_07_before_comma() {
    assert_eq!(before_comma("red, green"), "red");
    assert_eq!(before_comma("blue"), "blue");
}

#[test]
fn drill_08_through_colon() {
    assert_eq!(through_colon("key: value"), "key:");
    assert_eq!(through_colon("none"), "none");
}
