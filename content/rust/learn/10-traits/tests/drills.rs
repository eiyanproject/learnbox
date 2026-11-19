#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_dog_sound() {
    assert_eq!(Dog.sound(), "woof");
}

#[test]
fn drill_02_cat_sound() {
    assert_eq!(Cat.sound(), "meow");
}

#[test]
fn drill_03_twice() {
    assert_eq!(twice(&Dog), "woof woof");
    assert_eq!(twice(&Cat), "meow meow");
}

#[test]
fn drill_04_chorus() {
    let animals: Vec<Box<dyn Animal>> = vec![Box::new(Dog), Box::new(Cat)];
    assert_eq!(chorus(&animals), vec!["woof", "meow"]);
}

#[test]
fn drill_05_display_dog() {
    assert_eq!(format!("{}", Dog), "a dog");
}

#[test]
fn drill_06_two_decimals() {
    assert_eq!(two_decimals(3.14159), "3.14");
    assert_eq!(two_decimals(2.0), "2.00");
}

#[test]
fn drill_07_bigger() {
    assert_eq!(bigger(3, 8), 8);
    assert_eq!(bigger(2.5, 1.0), 2.5);
    assert_eq!(bigger("pear", "apple"), "pear");
}

#[test]
fn drill_08_loud() {
    assert_eq!(Dog.loud(), "WOOF!");
    assert_eq!(Cat.loud(), "MEOW!");
}

#[test]
fn drill_09_sum_all() {
    assert_eq!(sum_all(&[1.5, 2.5]), 4.0);
    assert_eq!(sum_all(&[]), 0.0);
}
