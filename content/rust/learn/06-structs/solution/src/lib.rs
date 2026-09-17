#[derive(Debug, Clone, PartialEq)]
pub struct Rectangle {
    pub width: u32,
    pub height: u32,
}

impl Rectangle {
    pub fn new(width: u32, height: u32) -> Self {
        Self { width, height }
    }

    pub fn square(size: u32) -> Self {
        Self::new(size, size)
    }

    pub fn area(&self) -> u32 {
        self.width * self.height
    }

    pub fn perimeter(&self) -> u32 {
        2 * (self.width + self.height)
    }

    pub fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }

    pub fn scale(&mut self, factor: u32) {
        self.width *= factor;
        self.height *= factor;
    }
}
