use arena_inventory::*;

fn stocked() -> Inventory {
    let mut inv = Inventory::new();
    inv.add("widget", 3, 250);
    inv.add("bolt", 100, 5);
    inv.add("anvil", 1, 12000);
    inv
}

#[test]
fn starts_empty() {
    let inv = Inventory::new();
    assert_eq!(inv.total_value(), 0);
    assert!(inv.get("widget").is_none());
    assert!(inv.low_stock(10).is_empty());
    assert!(inv.most_valuable().is_none());
}

#[test]
fn add_then_get() {
    let inv = stocked();
    assert_eq!(inv.get("widget"), Some(&Item { name: "widget".to_string(), qty: 3, price_cents: 250 }));
    assert!(inv.get("Widget").is_none());
}

#[test]
fn adding_again_adds_stock_and_replaces_the_price() {
    let mut inv = stocked();
    inv.add("widget", 2, 300);
    let widget = inv.get("widget").unwrap();
    assert_eq!((widget.qty, widget.price_cents), (5, 300));
}

#[test]
fn remove_returns_what_is_left() {
    let mut inv = stocked();
    assert_eq!(inv.remove("widget", 1), Ok(2));
    assert_eq!(inv.remove("widget", 2), Ok(0));
    assert_eq!(inv.get("widget").unwrap().qty, 0);
}

#[test]
fn an_item_at_zero_is_still_known() {
    let mut inv = stocked();
    inv.remove("anvil", 1).unwrap();
    assert!(inv.get("anvil").is_some());
    assert_eq!(inv.remove("anvil", 1), Err(InventoryError::Insufficient { have: 0, wanted: 1 }));
    assert_eq!(inv.remove("anvil", 0), Ok(0));
}

#[test]
fn removing_too_many_takes_nothing() {
    let mut inv = stocked();
    assert_eq!(inv.remove("widget", 4), Err(InventoryError::Insufficient { have: 3, wanted: 4 }));
    assert_eq!(inv.get("widget").unwrap().qty, 3);
}

#[test]
fn removing_what_was_never_there() {
    let mut inv = stocked();
    assert_eq!(inv.remove("gizmo", 1), Err(InventoryError::Unknown("gizmo".to_string())));
}

#[test]
fn total_value() {
    let mut inv = stocked();
    assert_eq!(inv.total_value(), 3 * 250 + 100 * 5 + 12000);
    inv.remove("bolt", 40).unwrap();
    assert_eq!(inv.total_value(), 3 * 250 + 60 * 5 + 12000);
}

#[test]
fn total_value_does_not_overflow_u32() {
    let mut inv = Inventory::new();
    inv.add("gold", 4_000_000_000, 5_000);
    assert_eq!(inv.total_value(), 20_000_000_000_000);
}

#[test]
fn low_stock_is_sorted_and_strictly_below() {
    let mut inv = stocked();
    assert_eq!(inv.low_stock(4), vec!["anvil", "widget"]);
    assert_eq!(inv.low_stock(3), vec!["anvil"]);
    assert_eq!(inv.low_stock(1), Vec::<&str>::new());
    inv.remove("bolt", 100).unwrap();
    assert_eq!(inv.low_stock(1), vec!["bolt"]);
}

#[test]
fn most_valuable_is_by_stock_value() {
    let mut inv = stocked();
    assert_eq!(inv.most_valuable().unwrap().name, "anvil");
    inv.remove("anvil", 1).unwrap();
    assert_eq!(inv.most_valuable().unwrap().name, "widget");
}

#[test]
fn most_valuable_ties_go_alphabetically() {
    let mut inv = Inventory::new();
    inv.add("pear", 2, 50);
    inv.add("apple", 1, 100);
    inv.add("zest", 4, 25);
    assert_eq!(inv.most_valuable().unwrap().name, "apple");
}

#[test]
fn display() {
    let inv = stocked();
    assert_eq!(inv.get("widget").unwrap().to_string(), "widget x3 @ 2.50");
    assert_eq!(inv.get("bolt").unwrap().to_string(), "bolt x100 @ 0.05");
    assert_eq!(inv.get("anvil").unwrap().to_string(), "anvil x1 @ 120.00");
}

#[test]
fn borrowed_views_do_not_stop_later_changes() {
    let mut inv = stocked();
    let low: Vec<String> = inv.low_stock(4).into_iter().map(String::from).collect();
    for name in &low {
        inv.add(name, 10, 1);
    }
    assert!(inv.low_stock(4).is_empty());
}
