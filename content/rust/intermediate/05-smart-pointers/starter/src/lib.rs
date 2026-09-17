use std::cell::RefCell;
use std::fmt;
use std::rc::Rc;

pub enum Expr {
    Num(f64),
    // Add, Mul and Neg need Box to be recursive.
}

impl Expr {
    pub fn eval(&self) -> f64 {
        todo!()
    }
}

// impl fmt::Display for Expr { ... }

pub fn num(n: f64) -> Expr {
    Expr::Num(n)
}

// pub fn add(a: Expr, b: Expr) -> Expr
// pub fn mul(a: Expr, b: Expr) -> Expr
// pub fn neg(a: Expr) -> Expr

pub struct SharedLog {
    entries: Rc<RefCell<Vec<String>>>,
}

impl SharedLog {
    pub fn new() -> Self {
        todo!()
    }

    // clone_handle, push, try_push, entries, handle_count

    /// Runs `f` while holding a shared borrow of the entries (used to test try_push).
    /// Provided: leave as is.
    pub fn with_entries<R>(&self, f: impl FnOnce(&[String]) -> R) -> R {
        f(&self.entries.borrow())
    }
}
