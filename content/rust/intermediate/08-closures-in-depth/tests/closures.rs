use closures_in_depth::*;

#[test]
fn event_bus_calls_handlers_in_order() {
    let mut bus = EventBus::new();
    let prefix = String::from(">> ");
    bus.on("login", move |user| format!("{prefix}welcome {user}"));
    bus.on("login", |user| user.to_uppercase());
    bus.on("logout", |user| format!("bye {user}"));
    assert_eq!(bus.emit("login", "ana"), [">> welcome ana", "ANA"]);
    assert_eq!(bus.emit("logout", "ana"), ["bye ana"]);
    assert!(bus.emit("unknown", "x").is_empty());
    assert_eq!(bus.handler_count("login"), 2);
    assert_eq!(bus.handler_count("nothing"), 0);
}

#[test]
fn counters_are_independent() {
    let mut a = make_counter();
    let mut b = make_counter();
    assert_eq!((a(), a(), a()), (1, 2, 3));
    assert_eq!(b(), 1);
}

#[test]
fn apply_twice_accepts_fnmut() {
    let mut calls = 0;
    let result = apply_twice(
        |x| {
            calls += 1;
            x * 3
        },
        2,
    );
    assert_eq!(result, 18);
    assert_eq!(calls, 2);
    assert_eq!(apply_twice(|x| x + 1, 0), 2);
}

#[test]
fn run_once_accepts_fnonce() {
    let owned = String::from("moved out");
    assert_eq!(run_once(move || owned), "moved out");
    assert_eq!(run_once(|| "plain".to_string()), "plain");
}

#[test]
fn compose_functions() {
    let add_then_double = compose(|x| x + 1, |x| x * 2);
    assert_eq!(add_then_double(3), 8);
    let offset = 10;
    let shifted = compose(move |x| x - offset, i32::abs);
    assert_eq!(shifted(4), 6);
}
