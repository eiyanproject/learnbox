use hello_cargo::*;

#[test]
fn greets_by_name() {
    assert_eq!(greeting("Ana"), "Hello, Ana!");
}

#[test]
fn greets_another_name() {
    assert_eq!(greeting("Rustacean"), "Hello, Rustacean!");
}

#[test]
fn banner_short_title() {
    assert_eq!(banner("hi"), "==\nhi\n==");
}

#[test]
fn banner_long_title() {
    assert_eq!(banner("learnbox"), "========\nlearnbox\n========");
}
