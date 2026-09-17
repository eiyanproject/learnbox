use std::any::Any;

use trait_objects::*;

fn registry() -> Registry {
    let mut r = Registry::new();
    r.register(Box::new(Counter { calls: 0 }));
    r.register(Box::new(Uppercase));
    r.register(Box::new(Suffix("!".into())));
    r
}

#[test]
fn names_in_order() {
    assert_eq!(registry().names(), ["counter", "upper", "suffix"]);
}

#[test]
fn pipeline_through_trait_objects() {
    let mut r = registry();
    assert_eq!(r.run_all("hello"), "HELLO!");
    assert_eq!(r.run_all("again"), "AGAIN!");
}

#[test]
fn find_by_concrete_type() {
    let mut r = registry();
    r.run_all("a");
    r.run_all("b");
    let counter: &Counter = r.find::<Counter>().expect("a Counter is registered");
    assert_eq!(counter.calls, 2);
    assert_eq!(r.find::<Suffix>().map(|s| s.0.as_str()), Some("!"));
}

#[test]
fn find_missing_type() {
    let mut r = Registry::new();
    r.register(Box::new(Uppercase));
    assert!(r.find::<Counter>().is_none());
    assert_eq!(Registry::new().run_all("unchanged"), "unchanged");
}

#[test]
fn user_defined_plugins_work() {
    struct Reverse;
    impl Plugin for Reverse {
        fn name(&self) -> &str {
            "reverse"
        }
        fn run(&mut self, input: &str) -> String {
            input.chars().rev().collect()
        }
        fn as_any(&self) -> &dyn Any {
            self
        }
    }
    let mut r = registry();
    r.register(Box::new(Reverse));
    assert_eq!(r.run_all("ab"), "!BA");
}

#[test]
fn describe_any() {
    assert_eq!(describe_value(&42i32), "i32 42");
    assert_eq!(describe_value(&String::from("hello")), "String hello");
    assert_eq!(describe_value(&"hi"), "&str hi");
    assert_eq!(describe_value(&4.5f64), "something else");
}
