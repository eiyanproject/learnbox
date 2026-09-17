pub mod circle;

use circle::Circle;

pub fn describe(c: &Circle) -> String {
    format!("circle r={} area={:.2}", c.radius(), c.area())
}
