use std::f64::consts::PI;
use std::fmt;

pub trait Shape {
    fn area(&self) -> f64;
    fn name(&self) -> String;

    // Add a default method here:
    // fn describe(&self) -> String { ... }
}

pub struct Circle {
    pub radius: f64,
}

pub struct Square {
    pub side: f64,
}

// impl Shape for Circle { ... }

// impl Shape for Square { ... }

// impl fmt::Display for Square { ... }

pub fn total_area(shapes: &[Box<dyn Shape>]) -> f64 {
    todo!()
}

pub fn largest<T: PartialOrd + Copy>(items: &[T]) -> T {
    todo!()
}
