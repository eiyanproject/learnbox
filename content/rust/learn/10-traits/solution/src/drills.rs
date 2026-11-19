// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, then press that drill's Run button in the
// Results tab: it builds and tests just that drill, so a mistake in one never
// stops the others. Keep the `/// Drill N:` lines; they mark where each drill
// starts. The hidden tests read this file directly, so it needs no `mod` line.

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
        "woof".to_string()
    }
}

/// Drill 2: `Cat.sound()` is `"meow"`
impl Animal for Cat {
    fn sound(&self) -> String {
        "meow".to_string()
    }
}

/// Drill 3: `twice(&Dog)` is `"woof woof"`; any animal works
pub fn twice(animal: &impl Animal) -> String {
    let s = animal.sound();
    format!("{s} {s}")
}

/// Drill 4: `chorus(&[Box::new(Dog), Box::new(Cat)])` is `vec!["woof", "meow"]`; any animals work
pub fn chorus(animals: &[Box<dyn Animal>]) -> Vec<String> {
    let mut out = Vec::new();
    for a in animals {
        out.push(a.sound());
    }
    out
}

/// Drill 5: `format!("{}", Dog)` is `"a dog"`
impl fmt::Display for Dog {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "a dog")
    }
}

/// Drill 6: `two_decimals(3.14159)` is `"3.14"`
pub fn two_decimals(x: f64) -> String {
    format!("{x:.2}")
}

/// Drill 7: `bigger(3, 8)` is `8`, and works for `f64` and `&str` too
pub fn bigger<T: PartialOrd>(a: T, b: T) -> T {
    if a > b { a } else { b }
}

/// Drill 8: an animal that says `moo` gets `loud()` for free, giving `"MOO!"`: write the trait's **default** method once
pub trait Loud: Animal {
    fn loud(&self) -> String {
        self.sound().to_uppercase() + "!"
    }
}

/// Drill 9: `sum_all(&[1.5, 2.5])` is `4.0`
pub fn sum_all(values: &[f64]) -> f64 {
    values.iter().sum()
}
