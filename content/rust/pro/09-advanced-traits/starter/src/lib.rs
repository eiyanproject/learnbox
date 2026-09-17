pub trait LendingIterator {
    // type Item<'a> where Self: 'a;
    // fn next(&mut self) -> Option<Self::Item<'_>>;
}

pub struct WindowsMut<'a> {
    data: &'a mut [i32],
    size: usize,
    start: usize,
}

impl<'a> WindowsMut<'a> {
    pub fn new(data: &'a mut [i32], size: usize) -> Self {
        WindowsMut { data, size, start: 0 }
    }
}

// impl LendingIterator for WindowsMut<'_>

pub trait Pipeline {
    // fn steps(&self) -> impl Iterator<Item = &str>;
}

pub struct Simple {
    pub steps: Vec<String>,
}

pub trait Repository {
    // name, find, all (dyn-compatible)
}

pub struct MemoryRepo {
    pub name: String,
    pub items: Vec<String>,
}

pub fn count_all(repos: &[Box<dyn Repository>]) -> usize {
    todo!()
}

pub fn total_len<I>(items: I) -> usize {
    todo!()
}
