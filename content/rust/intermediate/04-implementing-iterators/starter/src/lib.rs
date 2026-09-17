pub struct Fibonacci {
    // your state here
}

impl Fibonacci {
    pub fn new() -> Self {
        todo!()
    }
}

// impl Iterator for Fibonacci { ... }

pub struct Countdown {
    // your state here
}

impl Countdown {
    pub fn new(n: u32) -> Self {
        todo!()
    }
}

// impl Iterator for Countdown { ... }
// impl DoubleEndedIterator for Countdown { ... }

pub struct Ring<T> {
    pub items: Vec<T>,
}

// impl<'a, T> IntoIterator for &'a Ring<T> { ... }
// impl<T> IntoIterator for Ring<T> { ... }

// pub struct EveryNthIter<I> { ... }
// impl<I: Iterator> Iterator for EveryNthIter<I> { ... }
// pub trait EveryNth: Iterator + Sized { ... }
// impl<I: Iterator> EveryNth for I {}
