use std::f64::consts::PI;
use std::fmt;

pub trait Shape {
    fn area(&self) -> f64;
    fn name(&self) -> String;

    fn describe(&self) -> String {
        format!("{} with area {:.2}", self.name(), self.area())
    }
}

pub struct Circle {
    pub radius: f64,
}

pub struct Square {
    pub side: f64,
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        PI * self.radius * self.radius
    }

    fn name(&self) -> String {
        "circle".to_string()
    }
}

impl Shape for Square {
    fn area(&self) -> f64 {
        self.side * self.side
    }

    fn name(&self) -> String {
        "square".to_string()
    }
}

impl fmt::Display for Square {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Square({})", self.side)
    }
}

pub fn total_area(shapes: &[Box<dyn Shape>]) -> f64 {
    let mut total = 0.0;
    for shape in shapes {
        total += shape.area();
    }
    total
}

pub fn largest<T: PartialOrd + Copy>(items: &[T]) -> T {
    let mut best = items[0];
    for &item in items {
        if item > best {
            best = item;
        }
    }
    best
}
