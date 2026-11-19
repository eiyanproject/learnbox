#![allow(dead_code)]

include!("../src/drills.rs");

#[test]
fn drill_01_origin() {
    assert_eq!(origin(), Point { x: 0, y: 0 });
}

#[test]
fn drill_02_point() {
    assert_eq!(point(3, 4), Point { x: 3, y: 4 });
}

#[test]
fn drill_03_sum_of() {
    assert_eq!(sum_of(&Point { x: 3, y: 4 }), 7);
}

#[test]
fn drill_04_move_right() {
    let mut p = Point { x: 0, y: 5 };
    move_right(&mut p);
    assert_eq!(p, Point { x: 1, y: 5 });
}

#[test]
fn drill_05_new() {
    assert_eq!(Point::new(1, 2), Point { x: 1, y: 2 });
}

#[test]
fn drill_06_distance() {
    assert_eq!(Point::new(-3, 4).distance(), 7);
}

#[test]
fn drill_07_shift() {
    let mut p = Point::new(1, 1);
    p.shift(2, -1);
    assert_eq!(p, Point::new(3, 0));
}

#[test]
fn drill_08_into_pair() {
    assert_eq!(Point::new(5, 6).into_pair(), (5, 6));
}

#[test]
fn drill_09_debug_text() {
    assert_eq!(debug_text(&Point::new(1, 2)), "Point { x: 1, y: 2 }");
}
