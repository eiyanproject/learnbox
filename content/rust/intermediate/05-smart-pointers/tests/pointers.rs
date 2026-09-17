use smart_pointers::*;

#[test]
fn expression_eval() {
    let e = mul(add(num(1.0), num(2.0)), neg(num(3.0)));
    assert_eq!(e.eval(), -9.0);
    assert_eq!(num(2.5).eval(), 2.5);
}

#[test]
fn expression_display() {
    let e = mul(add(num(1.0), num(2.0)), neg(num(3.0)));
    assert_eq!(e.to_string(), "((1 + 2) * -3)");
    assert_eq!(add(num(0.5), mul(num(2.0), num(4.0))).to_string(), "(0.5 + (2 * 4))");
}

#[test]
fn deep_expression() {
    let mut e = num(0.0);
    for i in 1..=1000 {
        e = add(e, num(i as f64));
    }
    assert_eq!(e.eval(), 500500.0);
}

#[test]
fn shared_log_handles_see_the_same_entries() {
    let log = SharedLog::new();
    let a = log.clone_handle();
    let b = a.clone_handle();
    assert_eq!(log.handle_count(), 3);
    a.push("from a");
    b.push("from b");
    log.push("from log");
    assert_eq!(log.entries(), ["from a", "from b", "from log"]);
    drop(a);
    assert_eq!(b.handle_count(), 2);
}

#[test]
fn try_push_does_not_panic_while_borrowed() {
    let log = SharedLog::new();
    let other = log.clone_handle();
    log.push("first");
    let pushed_during_borrow = log.with_entries(|entries| {
        assert_eq!(entries.len(), 1);
        other.try_push("while reading")
    });
    assert!(!pushed_during_borrow);
    assert!(other.try_push("after"));
    assert_eq!(log.entries(), ["first", "after"]);
}
