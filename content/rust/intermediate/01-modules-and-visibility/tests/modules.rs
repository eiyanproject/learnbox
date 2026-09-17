use modules_lesson::Circle;
use modules_lesson::shapes;

#[test]
fn reexport_is_the_same_type() {
    let c: modules_lesson::shapes::circle::Circle = Circle::new(2.0);
    assert_eq!(c.radius(), 2.0);
}

#[test]
fn area_and_circumference_are_rounded() {
    let c = Circle::new(1.0);
    assert_eq!(c.area(), 3.14);
    assert_eq!(c.circumference(), 6.28);
    assert_eq!(Circle::new(1.5).area(), 7.07);
}

#[test]
fn describe_lives_in_shapes() {
    assert_eq!(shapes::describe(&Circle::new(1.5)), "circle r=1.5 area=7.07");
}
