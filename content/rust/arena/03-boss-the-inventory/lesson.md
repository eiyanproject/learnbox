---
title: "Boss: The inventory"
summary: A stock room as a type, with borrowed views into it, errors that carry their reasons and a Display impl.
order: 4
files: [src/lib.rs]
run: cargo test
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 1800
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **boss round** | the longest arena round, combining several lessons |
| **inventory** | the stock room: items with a quantity and a price |
| **item** | one product: name, quantity, price in cents |
| **cents** | prices are stored as whole cents to avoid decimal errors |
| **total value** | the sum of quantity times price over every item |
| **low stock** | fewer than the threshold in stock, strictly below |
| **tie-break** | when several items are worth the same, the one first alphabetically |
| **borrowed view** | a `&Item` or `&str` into the inventory; it must end when the method returns |
| **widen before multiplying** | convert `qty` to `u64` so large totals do not overflow |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs this round's tests |

### Rust names

| Name | What it does |
|---|---|
| `Inventory::new()`, `add`, `remove`, `get` | the basic operations |
| `total_value`, `low_stock`, `most_valuable` | the questions |
| `InventoryError::Unknown(String)`, `InventoryError::Insufficient { have, wanted }` | the given errors |
| `BTreeMap<String, Item>` | keeps names in alphabetical order |
| `map.entry(name.to_string()).or_insert(...)` | add or update one item |
| `map.get(name)`, `map.get_mut(name)` | borrow an item, to read or change |
| `item.qty as u64 * item.price_cents as u64` | the item's value without overflow |
| `.max_by(\|a, b\| ...)`, `.then_with(...)` | the most valuable, with a tie-break |
| `impl fmt::Display for Item` | `widget x3 @ 2.50` |
| `write!(f, "{}.{:02}", c / 100, c % 100)` | whole units and two-digit cents |

### Errors

| Error | Means |
|---|---|
| `Unknown(name)` | a name that was never added |
| `Insufficient { have: 0, wanted: 1 }` | not enough stock; nothing is taken |
| `attempt to multiply with overflow` | a debug-build panic from multiplying in `u32` |

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

## Details the tests check

- Names are case-sensitive: after adding `"widget"`, `get("Widget")` is
  `None`.
- `total_value` can exceed what a `u32` holds (4,000,000,000 items at 5,000
  cents is 20,000,000,000,000), so convert `qty` to `u64` before
  multiplying.
- `low_stock(threshold)` is strictly below: with `widget` at 3,
  `low_stock(3)` does not include it, `low_stock(4)` does.
- An item at 0 is still known: removing 1 more is
  `Insufficient { have: 0, wanted: 1 }`, and removing 0 is `Ok(0)`.
- Prices print as whole units, a dot and exactly two digits: 5 cents is
  `0.05`, 12000 cents is `120.00`.
- The test `borrowed_views_do_not_stop_later_changes` copies the names from
  `low_stock` into `String`s and then calls `add`. Your methods' borrows must
  end when they return, which they will if the signatures are left as given.

Which collection holds the items is up to you. A `HashMap<String, Item>`
makes `add`, `remove` and `get` direct; a `BTreeMap<String, Item>` also keeps
the names in alphabetical order, which `low_stock` and the tie-break in
`most_valuable` both need.
