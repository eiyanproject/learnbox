pub enum Shape {
    Circle { radius: f64 },
    Square(f64),
    Rectangle { width: f64, height: f64 },
}

impl Shape {
    pub fn area(&self) -> f64 {
        match self {
            Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
            Shape::Square(side) => side * side,
            Shape::Rectangle { width, height } => width * height,
        }
    }
}

pub enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

pub fn value_in_cents(coin: Coin) -> u32 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}

pub fn classify(n: i32) -> &'static str {
    match n {
        0 => "zero",
        1..=9 => "small",
        n if n < 0 => "negative",
        _ => "large",
    }
}

pub enum Command {
    Move { x: i32, y: i32 },
    Say(String),
    Quit,
}

pub fn describe(cmd: &Command) -> String {
    match cmd {
        Command::Move { x, y } => format!("move to {x},{y}"),
        Command::Say(text) => format!("say {text}"),
        Command::Quit => "quit".to_string(),
    }
}
