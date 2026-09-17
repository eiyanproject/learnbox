use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, RwLock};

#[derive(Clone)]
pub struct BankAccount {
    pub id: u32,
    balance: Arc<Mutex<i64>>,
}

impl BankAccount {
    pub fn new(id: u32, balance: i64) -> Self {
        BankAccount { id, balance: Arc::new(Mutex::new(balance)) }
    }

    pub fn deposit(&self, amount: i64) {
        *self.balance.lock().unwrap() += amount;
    }

    pub fn withdraw(&self, amount: i64) -> bool {
        let mut balance = self.balance.lock().unwrap();
        if *balance < amount {
            return false;
        }
        *balance -= amount;
        true
    }

    pub fn balance(&self) -> i64 {
        *self.balance.lock().unwrap()
    }
}

pub fn transfer(from: &BankAccount, to: &BankAccount, amount: i64) -> bool {
    if Arc::ptr_eq(&from.balance, &to.balance) {
        return from.balance() >= amount;
    }
    // Always lock the lower id first, whichever direction the money moves.
    let (first, second) = if from.id < to.id { (from, to) } else { (to, from) };
    let mut a = first.balance.lock().unwrap();
    let mut b = second.balance.lock().unwrap();
    let (from_bal, to_bal) = if from.id < to.id { (&mut *a, &mut *b) } else { (&mut *b, &mut *a) };
    if *from_bal < amount {
        return false;
    }
    *from_bal -= amount;
    *to_bal += amount;
    true
}

#[derive(Clone)]
pub struct HitCounter {
    hits: Arc<AtomicU64>,
}

impl HitCounter {
    pub fn new() -> Self {
        HitCounter { hits: Arc::new(AtomicU64::new(0)) }
    }

    pub fn hit(&self) {
        self.hits.fetch_add(1, Ordering::Relaxed);
    }

    pub fn total(&self) -> u64 {
        self.hits.load(Ordering::Relaxed)
    }
}

#[derive(Clone)]
pub struct ConfigStore {
    values: Arc<RwLock<HashMap<String, String>>>,
}

impl ConfigStore {
    pub fn new() -> Self {
        ConfigStore { values: Arc::new(RwLock::new(HashMap::new())) }
    }

    pub fn get(&self, key: &str) -> Option<String> {
        self.values.read().unwrap().get(key).cloned()
    }

    pub fn set(&self, key: &str, value: &str) {
        self.values.write().unwrap().insert(key.to_string(), value.to_string());
    }
}
