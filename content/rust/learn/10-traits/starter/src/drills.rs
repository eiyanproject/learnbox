// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, press Check, and that drill gets its own
// tick in the Results tab. The hidden tests read this file directly, so it
// needs no `mod` line anywhere.

use std::fmt;

/// Something that makes a sound. Already written: read it first.
pub trait Animal {
    fn sound(&self) -> String;
}

pub struct Dog;
pub struct Cat;

/// Drill 1: `Dog.sound()` is `"woof"`
impl Animal for Dog {
    fn sound(&self) -> String {
        todo!()
    }
}

/// Drill 2: `Cat.sound()` is `"meow"`
impl Animal for Cat {
    fn sound(&self) -> String {
        todo!()
    }
}

/// Drill 3: `twice(&Dog)` is `"woof woof"`
pub fn twice(animal: &impl Animal) -> String {
    todo!()
}

/// Drill 4: `chorus(&[Box::new(Dog), Box::new(Cat)])` is `vec!["woof", "meow"]`
pub fn chorus(animals: &[Box<dyn Animal>]) -> Vec<String> {
    todo!()
}

/// Drill 5: `format!("{}", Dog)` is `"a dog"`
impl fmt::Display for Dog {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        todo!()
    }
}

/// Drill 6: `two_decimals(3.14159)` is `"3.14"`
pub fn two_decimals(x: f64) -> String {
    todo!()
}

/// Drill 7: `bigger(3, 8)` is `8`, and works for `f64` and `&str` too
pub fn bigger<T: PartialOrd>(a: T, b: T) -> T {
    todo!()
}

/// Drill 8: `Dog.loud()` is `"WOOF!"`: write the trait's **default** method once, for every animal
pub trait Loud: Animal {
    fn loud(&self) -> String {
        todo!()
    }
}

impl Loud for Dog {}
impl Loud for Cat {}

/// Drill 9: `sum_all(&[1.5, 2.5])` is `4.0`
pub fn sum_all(values: &[f64]) -> f64 {
    todo!()
}
