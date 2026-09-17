use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use shared_state::*;

#[test]
fn account_basics() {
    let acc = BankAccount::new(1, 100);
    acc.deposit(50);
    assert!(acc.withdraw(120));
    assert!(!acc.withdraw(31));
    assert_eq!(acc.balance(), 30);
}

#[test]
fn clones_share_the_balance() {
    let acc = BankAccount::new(1, 0);
    let handles: Vec<_> = (0..8)
        .map(|_| {
            let acc = acc.clone();
            thread::spawn(move || {
                for _ in 0..1000 {
                    acc.deposit(1);
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    assert_eq!(acc.balance(), 8000);
}

#[test]
fn concurrent_withdrawals_never_overdraw() {
    let acc = BankAccount::new(1, 1000);
    let handles: Vec<_> = (0..10)
        .map(|_| {
            let acc = acc.clone();
            thread::spawn(move || (0..200).filter(|_| acc.withdraw(1)).count())
        })
        .collect();
    let succeeded: usize = handles.into_iter().map(|h| h.join().unwrap()).sum();
    assert_eq!(succeeded, 1000);
    assert_eq!(acc.balance(), 0);
}

#[test]
fn transfer_moves_money() {
    let a = BankAccount::new(1, 100);
    let b = BankAccount::new(2, 0);
    assert!(transfer(&a, &b, 70));
    assert!(!transfer(&a, &b, 31));
    assert_eq!((a.balance(), b.balance()), (30, 70));
}

#[test]
fn opposite_transfers_do_not_deadlock() {
    let a = BankAccount::new(1, 10_000);
    let b = BankAccount::new(2, 10_000);
    let (done_tx, done_rx) = mpsc::channel();
    for flip in [false, true] {
        let (a, b, done_tx) = (a.clone(), b.clone(), done_tx.clone());
        thread::spawn(move || {
            for _ in 0..20_000 {
                if flip {
                    transfer(&b, &a, 1);
                } else {
                    transfer(&a, &b, 1);
                }
            }
            done_tx.send(()).unwrap();
        });
    }
    for _ in 0..2 {
        done_rx.recv_timeout(Duration::from_secs(20)).expect("transfers deadlocked");
    }
    assert_eq!(a.balance() + b.balance(), 20_000);
}

#[test]
fn hit_counter() {
    let c = HitCounter::new();
    let handles: Vec<_> = (0..4)
        .map(|_| {
            let c = c.clone();
            thread::spawn(move || {
                for _ in 0..25_000 {
                    c.hit();
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    assert_eq!(c.total(), 100_000);
}

#[test]
fn hit_counter_is_lock_free() {
    let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    assert!(src.contains("AtomicU64"));
}

#[test]
fn config_store() {
    let store = ConfigStore::new();
    let writer = store.clone();
    thread::spawn(move || writer.set("theme", "dark")).join().unwrap();
    assert_eq!(store.get("theme").as_deref(), Some("dark"));
    assert_eq!(store.get("missing"), None);
}
