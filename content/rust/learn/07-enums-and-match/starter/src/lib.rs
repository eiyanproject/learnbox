pub enum Shape {
    Circle { radius: f64 },
    Square(f64),
    Rectangle { width: f64, height: f64 },
}

impl Shape {
    pub fn area(&self) -> f64 {
        todo!()
    }
}

pub enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

pub fn value_in_cents(coin: Coin) -> u32 {
    todo!()
}

pub fn classify(n: i32) -> &'static str {
    todo!()
}

pub enum Command {
    Move { x: i32, y: i32 },
    Say(String),
    Quit,
}

pub fn describe(cmd: &Command) -> String {
    todo!()
}
