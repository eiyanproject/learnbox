use std::fmt;
use std::ops::{Add, AddAssign, Mul, Neg, Sub};

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Money {
    pub cents: i64,
}

impl Money {
    pub fn new(cents: i64) -> Self {
        Money { cents }
    }
}

impl Add for Money {
    type Output = Money;
    fn add(self, rhs: Money) -> Money {
        Money::new(self.cents + rhs.cents)
    }
}

impl Sub for Money {
    type Output = Money;
    fn sub(self, rhs: Money) -> Money {
        Money::new(self.cents - rhs.cents)
    }
}

impl Mul<i64> for Money {
    type Output = Money;
    fn mul(self, k: i64) -> Money {
        Money::new(self.cents * k)
    }
}

impl Neg for Money {
    type Output = Money;
    fn neg(self) -> Money {
        Money::new(-self.cents)
    }
}

impl AddAssign for Money {
    fn add_assign(&mut self, rhs: Money) {
        self.cents += rhs.cents;
    }
}

impl fmt::Display for Money {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let sign = if self.cents < 0 { "-" } else { "" };
        let abs = self.cents.abs();
        write!(f, "{sign}{}.{:02}", abs / 100, abs % 100)
    }
}

pub struct Stack<T> {
    pub items: Vec<T>,
}

pub trait Container {
    type Item;

    fn get(&self, i: usize) -> Option<&Self::Item>;
    fn len(&self) -> usize;

    fn first(&self) -> Option<&Self::Item> {
        self.get(0)
    }

    fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

impl<T> Container for Stack<T> {
    type Item = T;

    fn get(&self, i: usize) -> Option<&T> {
        self.items.get(i)
    }

    fn len(&self) -> usize {
        self.items.len()
    }
}

pub fn total_len<A: Container, B: Container>(a: &A, b: &B) -> usize {
    a.len() + b.len()
}

pub trait Describe: fmt::Display {
    fn describe(&self) -> String {
        format!("<{}>", self)
    }
}

impl<T: fmt::Display> Describe for T {}
