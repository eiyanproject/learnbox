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

// Operators and Display for Money go here.

pub struct Stack<T> {
    pub items: Vec<T>,
}

pub trait Container {
    // type Item; get, len, and defaults first, is_empty
}

pub fn total_len<A: Container, B: Container>(a: &A, b: &B) -> usize {
    todo!()
}

// pub trait Describe: fmt::Display { ... }
// impl<T: fmt::Display> Describe for T {}
