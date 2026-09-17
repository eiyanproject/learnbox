use std::cell::Cell;
use std::collections::HashMap;

use declarative_macros::{count, hashmap, max_of, newtype};

#[test]
fn hashmap_literal() {
    let m = hashmap! { "a" => 1, "b" => 2, "c" => 3 };
    assert_eq!(m.len(), 3);
    assert_eq!(m["b"], 2);
    let trailing = hashmap! { 1 => "one", };
    assert_eq!(trailing[&1], "one");
    let empty: HashMap<String, u8> = hashmap! {};
    assert!(empty.is_empty());
}

#[test]
fn hashmap_is_hygienic() {
    let map = "caller's own variable";
    let m = hashmap! { "k" => map };
    assert_eq!(m["k"], "caller's own variable");
}

#[test]
fn max_of_many() {
    assert_eq!(max_of!(7), 7);
    assert_eq!(max_of!(3, 9, 2), 9);
    assert_eq!(max_of!(1.5, -2.0, 0.25, 1.75), 1.75);
    assert_eq!(max_of!("pear", "apple"), "pear");
}

#[test]
fn max_of_evaluates_each_argument_once() {
    let calls = Cell::new(0);
    let next = |v: i32| {
        calls.set(calls.get() + 1);
        v
    };
    assert_eq!(max_of!(next(1), next(5), next(3)), 5);
    assert_eq!(calls.get(), 3);
}

#[test]
fn count_tokens() {
    const N: usize = count!(a b c d);
    assert_eq!(N, 4);
    assert_eq!(count!(), 0);
    assert_eq!(count!((nested group) [counts] {as one}), 3);
}

newtype!(UserId, u64);
newtype!(Celsius, f64);

#[test]
fn newtypes() {
    let id = UserId(42);
    let copy = id;
    assert_eq!(id, copy);
    assert_eq!(UserId::from(7).0, 7);
    let t: Celsius = 21.5.into();
    assert_eq!(format!("{t:?}"), "Celsius(21.5)");
}
