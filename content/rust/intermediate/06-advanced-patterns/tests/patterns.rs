use patterns_in_depth::*;

#[test]
fn slices() {
    assert_eq!(describe_slice(&[]), "nothing");
    assert_eq!(describe_slice(&["a"]), "only a");
    assert_eq!(describe_slice(&["a", "b"]), "a to b (2 items)");
    assert_eq!(describe_slice(&["a", "b", "c"]), "a to c (3 items)");
}

#[test]
fn ages() {
    assert_eq!(classify_age(0), "newborn");
    assert_eq!(classify_age(1), "child");
    assert_eq!(classify_age(12), "child");
    assert_eq!(classify_age(13), "teenager aged 13");
    assert_eq!(classify_age(19), "teenager aged 19");
    assert_eq!(classify_age(20), "adult");
}

#[test]
fn key_values() {
    assert_eq!(parse_kv("name = Ana"), Some(("name", "Ana")));
    assert_eq!(parse_kv("url=http://x?a=b"), Some(("url", "http://x?a=b")));
    assert_eq!(parse_kv("empty ="), Some(("empty", "")));
    assert_eq!(parse_kv("no equals"), None);
    assert_eq!(parse_kv("  = value"), None);
}

#[test]
fn pairs() {
    assert_eq!(sum_pairs(&[1, 2, 3, 4, 5]), [3, 7, 5]);
    assert_eq!(sum_pairs(&[1, 2, 3, 4]), [3, 7]);
    assert_eq!(sum_pairs(&[]), Vec::<i32>::new());
}

fn order(items: usize, destination: Destination) -> Order {
    Order { id: 1, items: vec!["x".to_string(); items], destination }
}

#[test]
fn shipping() {
    let orders = vec![
        order(1, Destination::Domestic { express: true }),
        order(2, Destination::Domestic { express: false }),
        order(1, Destination::International { country: "SG".into() }),
        order(3, Destination::International { country: "JP".into() }),
        order(0, Destination::International { country: "JP".into() }),
        order(0, Destination::Domestic { express: true }),
    ];
    assert_eq!(total_shipping(&orders), 15 + 5 + 20 + 30);
    assert_eq!(total_shipping(&[]), 0);
}
