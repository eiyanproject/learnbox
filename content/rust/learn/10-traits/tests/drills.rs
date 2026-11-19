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
    struct Cow;
    impl Animal for Cow {
        fn sound(&self) -> String {
            "moo".to_string()
        }
    }
    assert_eq!(twice(&Cow), "moo moo");
}

#[test]
fn drill_04_chorus() {
    struct Cow;
    impl Animal for Cow {
        fn sound(&self) -> String {
            "moo".to_string()
        }
    }
    struct Owl;
    impl Animal for Owl {
        fn sound(&self) -> String {
            "hoot".to_string()
        }
    }
    let animals: Vec<Box<dyn Animal>> = vec![Box::new(Cow), Box::new(Owl)];
    assert_eq!(chorus(&animals), vec!["moo", "hoot"]);
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
    struct Cow;
    impl Animal for Cow {
        fn sound(&self) -> String {
            "moo".to_string()
        }
    }
    impl Loud for Cow {}
    assert_eq!(Cow.loud(), "MOO!");
}

#[test]
fn drill_09_sum_all() {
    assert_eq!(sum_all(&[1.5, 2.5]), 4.0);
    assert_eq!(sum_all(&[]), 0.0);
}
