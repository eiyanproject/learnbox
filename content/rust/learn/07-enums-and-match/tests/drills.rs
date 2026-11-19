#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_next_light() {
    assert_eq!(next_light(Light::Red), Light::Green);
    assert_eq!(next_light(Light::Green), Light::Yellow);
    assert_eq!(next_light(Light::Yellow), Light::Red);
}

#[test]
fn drill_02_seconds() {
    assert_eq!(seconds(&Light::Red), 30);
    assert_eq!(seconds(&Light::Yellow), 5);
    assert_eq!(seconds(&Light::Green), 25);
}

#[test]
fn drill_03_can_go() {
    assert!(can_go(&Light::Green));
    assert!(!can_go(&Light::Red));
}

#[test]
fn drill_04_size_word() {
    assert_eq!(size_word(0), "none");
    assert_eq!(size_word(3), "few");
    assert_eq!(size_word(4), "many");
}

#[test]
fn drill_05_is_fish() {
    assert!(is_fish(&Pet::Fish));
    assert!(!is_fish(&Pet::Dog("rex".to_string())));
}

#[test]
fn drill_06_lives() {
    assert_eq!(lives(&Pet::Cat { lives: 9 }), 9);
    assert_eq!(lives(&Pet::Fish), 1);
}

#[test]
fn drill_07_pet_text() {
    assert_eq!(pet_text(&Pet::Dog("rex".to_string())), "dog rex");
    assert_eq!(pet_text(&Pet::Cat { lives: 9 }), "cat with 9 lives");
    assert_eq!(pet_text(&Pet::Fish), "fish");
}

#[test]
fn drill_08_dog_name() {
    assert_eq!(dog_name(&Pet::Dog("rex".to_string())), "rex");
    assert_eq!(dog_name(&Pet::Fish), "");
}

#[test]
fn drill_09_is_red() {
    assert!(Light::Red.is_red());
    assert!(!Light::Green.is_red());
}
