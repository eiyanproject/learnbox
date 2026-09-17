use traits::*;

fn close(a: f64, b: f64) -> bool {
    (a - b).abs() < 1e-9
}

#[test]
fn areas_and_names() {
    let c = Circle { radius: 1.0 };
    let s = Square { side: 3.0 };
    assert!(close(c.area(), std::f64::consts::PI));
    assert!(close(s.area(), 9.0));
    assert_eq!(c.name(), "circle");
    assert_eq!(s.name(), "square");
}

#[test]
fn default_describe() {
    assert_eq!(Square { side: 2.0 }.describe(), "square with area 4.00");
    assert_eq!(Circle { radius: 1.0 }.describe(), "circle with area 3.14");
}

#[test]
fn display_square() {
    assert_eq!(Square { side: 2.0 }.to_string(), "Square(2)");
    assert_eq!(format!("{}", Square { side: 1.5 }), "Square(1.5)");
}

#[test]
fn total_area_of_mixed_shapes() {
    let shapes: Vec<Box<dyn Shape>> = vec![Box::new(Square { side: 2.0 }), Box::new(Circle { radius: 1.0 }), Box::new(Square { side: 1.0 })];
    assert!(close(total_area(&shapes), 5.0 + std::f64::consts::PI));
    assert!(close(total_area(&[]), 0.0));
}

#[test]
fn largest_works_for_many_types() {
    assert_eq!(largest(&[3, 9, 2]), 9);
    assert_eq!(largest(&[-1.5, -0.5]), -0.5);
    assert_eq!(largest(&['a', 'z', 'm']), 'z');
}
