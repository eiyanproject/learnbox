pub struct Fibonacci {
    curr: Option<u64>,
    next: Option<u64>,
}

impl Fibonacci {
    pub fn new() -> Self {
        Fibonacci { curr: Some(0), next: Some(1) }
    }
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<u64> {
        let out = self.curr?;
        let following = match (self.curr, self.next) {
            (Some(a), Some(b)) => a.checked_add(b),
            _ => None,
        };
        self.curr = self.next;
        self.next = following;
        Some(out)
    }
}

pub struct Countdown {
    front: u32,
    back: u32,
}

impl Countdown {
    pub fn new(n: u32) -> Self {
        Countdown { front: n, back: 1 }
    }

    fn remaining(&self) -> usize {
        if self.front >= self.back { (self.front - self.back + 1) as usize } else { 0 }
    }
}

impl Iterator for Countdown {
    type Item = u32;

    fn next(&mut self) -> Option<u32> {
        if self.remaining() == 0 {
            return None;
        }
        let v = self.front;
        self.front -= 1;
        Some(v)
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let n = self.remaining();
        (n, Some(n))
    }
}

impl DoubleEndedIterator for Countdown {
    fn next_back(&mut self) -> Option<u32> {
        if self.remaining() == 0 {
            return None;
        }
        let v = self.back;
        self.back += 1;
        Some(v)
    }
}

pub struct Ring<T> {
    pub items: Vec<T>,
}

impl<'a, T> IntoIterator for &'a Ring<T> {
    type Item = &'a T;
    type IntoIter = std::slice::Iter<'a, T>;

    fn into_iter(self) -> Self::IntoIter {
        self.items.iter()
    }
}

impl<T> IntoIterator for Ring<T> {
    type Item = T;
    type IntoIter = std::vec::IntoIter<T>;

    fn into_iter(self) -> Self::IntoIter {
        self.items.into_iter()
    }
}

pub struct EveryNthIter<I> {
    inner: I,
    n: usize,
    i: usize,
}

impl<I: Iterator> Iterator for EveryNthIter<I> {
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        loop {
            let item = self.inner.next()?;
            let keep = self.i % self.n == 0;
            self.i += 1;
            if keep {
                return Some(item);
            }
        }
    }
}

pub trait EveryNth: Iterator + Sized {
    fn every_nth(self, n: usize) -> EveryNthIter<Self> {
        assert!(n > 0, "n must be at least 1");
        EveryNthIter { inner: self, n, i: 0 }
    }
}

impl<I: Iterator> EveryNth for I {}
