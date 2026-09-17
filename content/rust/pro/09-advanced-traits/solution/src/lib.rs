pub trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;

    fn next(&mut self) -> Option<Self::Item<'_>>;
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

impl LendingIterator for WindowsMut<'_> {
    type Item<'s>
        = &'s mut [i32]
    where
        Self: 's;

    fn next(&mut self) -> Option<Self::Item<'_>> {
        if self.size == 0 || self.start + self.size > self.data.len() {
            return None;
        }
        let window = &mut self.data[self.start..self.start + self.size];
        self.start += 1;
        Some(window)
    }
}

pub trait Pipeline {
    fn steps(&self) -> impl Iterator<Item = &str>;

    fn describe(&self) -> String {
        self.steps().collect::<Vec<_>>().join(" -> ")
    }
}

pub struct Simple {
    pub steps: Vec<String>,
}

impl Pipeline for Simple {
    fn steps(&self) -> impl Iterator<Item = &str> {
        self.steps.iter().map(String::as_str)
    }
}

/// Dyn-compatible: `all` returns a boxed iterator instead of `impl Iterator`.
pub trait Repository {
    fn name(&self) -> &str;
    fn find(&self, id: usize) -> Option<String>;
    fn all(&self) -> Box<dyn Iterator<Item = String> + '_>;
}

pub struct MemoryRepo {
    pub name: String,
    pub items: Vec<String>,
}

impl Repository for MemoryRepo {
    fn name(&self) -> &str {
        &self.name
    }

    fn find(&self, id: usize) -> Option<String> {
        self.items.get(id).cloned()
    }

    fn all(&self) -> Box<dyn Iterator<Item = String> + '_> {
        Box::new(self.items.iter().cloned())
    }
}

pub fn count_all(repos: &[Box<dyn Repository>]) -> usize {
    repos.iter().map(|r| r.all().count()).sum()
}

pub fn total_len<I>(items: I) -> usize
where
    I: IntoIterator,
    I::Item: AsRef<str>,
{
    items.into_iter().map(|s| s.as_ref().len()).sum()
}
