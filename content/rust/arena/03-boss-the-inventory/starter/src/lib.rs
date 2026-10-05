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

#[derive(Debug, Default)]
pub struct Inventory {
    // your fields
}

impl Inventory {
    pub fn new() -> Self {
        todo!()
    }

    pub fn add(&mut self, name: &str, qty: u32, price_cents: u64) {
        todo!()
    }

    pub fn remove(&mut self, name: &str, qty: u32) -> Result<u32, InventoryError> {
        todo!()
    }

    pub fn get(&self, name: &str) -> Option<&Item> {
        todo!()
    }

    pub fn total_value(&self) -> u64 {
        todo!()
    }

    pub fn low_stock(&self, threshold: u32) -> Vec<&str> {
        todo!()
    }

    pub fn most_valuable(&self) -> Option<&Item> {
        todo!()
    }
}

impl fmt::Display for Item {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        todo!()
    }
}
