use variables_and_types::*;

fn close(a: f64, b: f64) -> bool {
    (a - b).abs() < 1e-9
}

#[test]
fn freezing_and_boiling() {
    assert!(close(celsius_to_fahrenheit(0.0), 32.0));
    assert!(close(celsius_to_fahrenheit(100.0), 212.0));
}

#[test]
fn body_temperature_keeps_the_fraction() {
    assert!(close(celsius_to_fahrenheit(37.0), 98.6));
    assert!(close(celsius_to_fahrenheit(-40.0), -40.0));
}

#[test]
fn hms_basic() {
    assert_eq!(seconds_to_hms(3725), (1, 2, 5));
}

#[test]
fn hms_edges() {
    assert_eq!(seconds_to_hms(0), (0, 0, 0));
    assert_eq!(seconds_to_hms(59), (0, 0, 59));
    assert_eq!(seconds_to_hms(86399), (23, 59, 59));
}

#[test]
fn average_with_fraction() {
    assert!(close(average(3, 4), 3.5));
    assert!(close(average(-3, 3), 0.0));
}

#[test]
fn average_does_not_overflow() {
    assert!(close(average(i32::MAX, i32::MAX), i32::MAX as f64));
}

#[test]
fn sums_an_array() {
    assert_eq!(sum_array([1, 2, 3, 4, 5]), 15);
    assert_eq!(sum_array([-10, 10, 0, 0, 7]), 7);
}
