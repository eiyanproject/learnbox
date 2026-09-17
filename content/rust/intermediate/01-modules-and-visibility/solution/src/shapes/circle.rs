use std::f64::consts::PI;

use crate::units::round2;

pub struct Circle {
    radius: f64,
}

impl Circle {
    pub fn new(radius: f64) -> Self {
        Circle { radius }
    }

    pub fn radius(&self) -> f64 {
        self.radius
    }

    pub fn area(&self) -> f64 {
        round2(PI * self.radius * self.radius)
    }

    pub fn circumference(&self) -> f64 {
        round2(2.0 * PI * self.radius)
    }
}
