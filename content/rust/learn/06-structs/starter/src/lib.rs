#[derive(Debug, Clone, PartialEq)]
pub struct Rectangle {
    pub width: u32,
    pub height: u32,
}

impl Rectangle {
    pub fn new(width: u32, height: u32) -> Self {
        todo!()
    }

    pub fn square(size: u32) -> Self {
        todo!()
    }

    pub fn area(&self) -> u32 {
        todo!()
    }

    pub fn perimeter(&self) -> u32 {
        todo!()
    }

    pub fn can_hold(&self, other: &Rectangle) -> bool {
        todo!()
    }

    // `scale` is missing. Add it: it multiplies both sides by `factor: u32`
    // and changes this rectangle.
}
