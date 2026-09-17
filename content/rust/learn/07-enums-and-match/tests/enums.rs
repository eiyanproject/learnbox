use enums_and_match::*;

fn close(a: f64, b: f64) -> bool {
    (a - b).abs() < 1e-9
}

#[test]
fn circle_area() {
    assert!(close(Shape::Circle { radius: 2.0 }.area(), std::f64::consts::PI * 4.0));
}

#[test]
fn square_and_rectangle_area() {
    assert!(close(Shape::Square(3.0).area(), 9.0));
    assert!(close(Shape::Rectangle { width: 2.5, height: 4.0 }.area(), 10.0));
}

#[test]
fn coins() {
    let total: u32 = [Coin::Penny, Coin::Nickel, Coin::Dime, Coin::Quarter]
        .into_iter()
        .map(value_in_cents)
        .sum();
    assert_eq!(total, 41);
    assert_eq!(value_in_cents(Coin::Quarter), 25);
}

#[test]
fn classify_numbers() {
    assert_eq!(classify(-7), "negative");
    assert_eq!(classify(0), "zero");
    assert_eq!(classify(1), "small");
    assert_eq!(classify(9), "small");
    assert_eq!(classify(10), "large");
}

#[test]
fn describe_commands() {
    assert_eq!(describe(&Command::Move { x: 3, y: -1 }), "move to 3,-1");
    assert_eq!(describe(&Command::Say("hello".to_string())), "say hello");
    assert_eq!(describe(&Command::Quit), "quit");
}
