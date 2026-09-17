use std::cell::RefCell;
use std::fmt;
use std::rc::Rc;

pub enum Expr {
    Num(f64),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
    Neg(Box<Expr>),
}

impl Expr {
    pub fn eval(&self) -> f64 {
        match self {
            Expr::Num(n) => *n,
            Expr::Add(a, b) => a.eval() + b.eval(),
            Expr::Mul(a, b) => a.eval() * b.eval(),
            Expr::Neg(a) => -a.eval(),
        }
    }
}

impl fmt::Display for Expr {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Expr::Num(n) => write!(f, "{n}"),
            Expr::Add(a, b) => write!(f, "({a} + {b})"),
            Expr::Mul(a, b) => write!(f, "({a} * {b})"),
            Expr::Neg(a) => write!(f, "-{a}"),
        }
    }
}

pub fn num(n: f64) -> Expr {
    Expr::Num(n)
}

pub fn add(a: Expr, b: Expr) -> Expr {
    Expr::Add(Box::new(a), Box::new(b))
}

pub fn mul(a: Expr, b: Expr) -> Expr {
    Expr::Mul(Box::new(a), Box::new(b))
}

pub fn neg(a: Expr) -> Expr {
    Expr::Neg(Box::new(a))
}

pub struct SharedLog {
    entries: Rc<RefCell<Vec<String>>>,
}

impl SharedLog {
    pub fn new() -> Self {
        SharedLog { entries: Rc::new(RefCell::new(Vec::new())) }
    }

    pub fn clone_handle(&self) -> SharedLog {
        SharedLog { entries: Rc::clone(&self.entries) }
    }

    pub fn push(&self, entry: &str) {
        self.entries.borrow_mut().push(entry.to_string());
    }

    pub fn try_push(&self, entry: &str) -> bool {
        match self.entries.try_borrow_mut() {
            Ok(mut v) => {
                v.push(entry.to_string());
                true
            }
            Err(_) => false,
        }
    }

    pub fn entries(&self) -> Vec<String> {
        self.entries.borrow().clone()
    }

    pub fn handle_count(&self) -> usize {
        Rc::strong_count(&self.entries)
    }

    /// Runs `f` while holding a shared borrow of the entries (used to test try_push).
    pub fn with_entries<R>(&self, f: impl FnOnce(&[String]) -> R) -> R {
        f(&self.entries.borrow())
    }
}
