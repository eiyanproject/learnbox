---
title: "Boss: The inventory"
summary: A stock room as a type, with borrowed views into it, errors that carry their reasons and a Display impl.
order: 3
files: [src/lib.rs]
run: cargo test
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 1800
---

The warehouse moves to the new system tonight. The stock room is the one
piece still missing, and the borrow checker is on shift.

## The task

`src/lib.rs` has the `Item` struct, the error enum and every signature. Fill
in the `Inventory` struct and the bodies. Do not change the signatures.

```rust
pub struct Item {
    pub name: String,
    pub qty: u32,
    pub price_cents: u64,
}

pub enum InventoryError {
    Unknown(String),
    Insufficient { have: u32, wanted: u32 },
}
```

- `Inventory::new()` is an empty stock room.
- `add(&mut self, name, qty, price_cents)` adds stock. A new name becomes a
  new item. For a name already there, `qty` is **added** to what is held
  and the price is **replaced**.
- `remove(&mut self, name, qty) -> Result<u32, InventoryError>` takes stock
  out and returns how many are left. A name that was never added is
  `Unknown(name)`. Asking for more than there is is `Insufficient` with what
  is held and what was wanted, and takes nothing. An item that reaches `0`
  stays in the inventory.
- `get(&self, name) -> Option<&Item>` borrows one item.
- `total_value(&self) -> u64` is the sum of `qty * price_cents` over
  everything.
- `low_stock(&self, threshold) -> Vec<&str>` is the names of the items with
  fewer than `threshold` in stock, in alphabetical order.
- `most_valuable(&self) -> Option<&Item>` is the item whose stock is worth
  the most (`qty * price_cents`). If several are level, the one that comes
  first alphabetically. `None` for an empty inventory.
- `Item` implements `Display` as name, quantity and price in whole units
  with two decimals: `widget x3 @ 2.50`.

```rust
let mut inv = Inventory::new();
inv.add("widget", 3, 250);
inv.add("bolt", 100, 5);
inv.remove("widget", 1);                 // Ok(2)
inv.total_value();                       // 1000
inv.low_stock(10);                       // ["widget"]
inv.get("widget").unwrap().to_string();  // "widget x2 @ 2.50"
```
