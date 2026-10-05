use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Item {
    pub name: String,
    pub qty: u32,
    pub price_cents: u64,
}

#[derive(Debug, PartialEq, Eq)]
pub enum InventoryError {
    Unknown(String),
    Insufficient { have: u32, wanted: u32 },
}

use std::cmp::Reverse;
use std::collections::BTreeMap;

#[derive(Debug, Default)]
pub struct Inventory {
    // A BTreeMap keeps the names sorted, which low_stock wants anyway.
    items: BTreeMap<String, Item>,
}

fn value(item: &Item) -> u64 {
    u64::from(item.qty) * item.price_cents
}

impl Inventory {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add(&mut self, name: &str, qty: u32, price_cents: u64) {
        let item = self.items.entry(name.to_string()).or_insert_with(|| Item { name: name.to_string(), qty: 0, price_cents });
        item.qty += qty;
        item.price_cents = price_cents;
    }

    pub fn remove(&mut self, name: &str, qty: u32) -> Result<u32, InventoryError> {
        let item = self.items.get_mut(name).ok_or_else(|| InventoryError::Unknown(name.to_string()))?;
        if qty > item.qty {
            return Err(InventoryError::Insufficient { have: item.qty, wanted: qty });
        }
        item.qty -= qty;
        Ok(item.qty)
    }

    pub fn get(&self, name: &str) -> Option<&Item> {
        self.items.get(name)
    }

    pub fn total_value(&self) -> u64 {
        self.items.values().map(value).sum()
    }

    pub fn low_stock(&self, threshold: u32) -> Vec<&str> {
        self.items.values().filter(|item| item.qty < threshold).map(|item| item.name.as_str()).collect()
    }

    pub fn most_valuable(&self) -> Option<&Item> {
        self.items.values().max_by_key(|item| (value(item), Reverse(item.name.as_str())))
    }
}

impl fmt::Display for Item {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} x{} @ {}.{:02}", self.name, self.qty, self.price_cents / 100, self.price_cents % 100)
    }
}
