use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, RwLock};

#[derive(Clone)]
pub struct BankAccount {
    pub id: u32,
    // balance: ...
}

impl BankAccount {
    pub fn new(id: u32, balance: i64) -> Self {
        todo!()
    }

    pub fn deposit(&self, amount: i64) {
        todo!()
    }

    pub fn withdraw(&self, amount: i64) -> bool {
        todo!()
    }

    pub fn balance(&self) -> i64 {
        todo!()
    }
}

pub fn transfer(from: &BankAccount, to: &BankAccount, amount: i64) -> bool {
    todo!()
}

#[derive(Clone)]
pub struct HitCounter {
    // hits: ...
}

impl HitCounter {
    pub fn new() -> Self {
        todo!()
    }

    pub fn hit(&self) {
        todo!()
    }

    pub fn total(&self) -> u64 {
        todo!()
    }
}

#[derive(Clone)]
pub struct ConfigStore {
    // values: ...
}

impl ConfigStore {
    pub fn new() -> Self {
        todo!()
    }

    pub fn get(&self, key: &str) -> Option<String> {
        todo!()
    }

    pub fn set(&self, key: &str, value: &str) {
        todo!()
    }
}
