use structs::Rectangle;

#[test]
fn new_sets_fields() {
    let r = Rectangle::new(3, 4);
    assert_eq!((r.width, r.height), (3, 4));
}

#[test]
fn square_has_equal_sides() {
    assert_eq!(Rectangle::square(5), Rectangle::new(5, 5));
}

#[test]
fn area_and_perimeter() {
    let r = Rectangle::new(3, 4);
    assert_eq!(r.area(), 12);
    assert_eq!(r.perimeter(), 14);
}

#[test]
fn can_hold_smaller() {
    assert!(Rectangle::new(8, 7).can_hold(&Rectangle::new(5, 1)));
}

#[test]
fn cannot_hold_larger_or_equal() {
    let r = Rectangle::new(8, 7);
    assert!(!r.can_hold(&Rectangle::new(9, 1)));
    assert!(!r.can_hold(&Rectangle::new(8, 7)));
    assert!(!Rectangle::new(5, 1).can_hold(&r));
}

#[test]
fn scale_changes_in_place() {
    let mut r = Rectangle::new(2, 3);
    r.scale(3);
    assert_eq!(r, Rectangle::new(6, 9));
}
