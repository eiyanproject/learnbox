// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, then press that drill's Run button in the
// Results tab: it builds and tests just that drill, so a mistake in one never
// stops the others. Keep the `/// Drill N:` lines; they mark where each drill
// starts. The hidden tests read this file directly, so it needs no `mod` line.

/// Two values of the same type. Already written: read it first.
#[derive(Debug, PartialEq)]
pub struct Pair<T> {
    pub a: T,
    pub b: T,
}

/// One value of any type.
pub struct Wrapper<T> {
    pub value: T,
}

/// Drill 1: `Pair::new(1, 2)` is `Pair { a: 1, b: 2 }`
impl<T> Pair<T> {
    pub fn new(a: T, b: T) -> Self {
        Pair { a, b }
    }
}

/// Drill 2: `Pair { a: 1, b: 2 }.swap()` is `Pair { a: 2, b: 1 }`
impl<T> Pair<T> {
    pub fn swap(self) -> Pair<T> {
        Pair { a: self.b, b: self.a }
    }
}

/// Drill 3: `Pair { a: 3, b: 9 }.larger()` is `9`
impl<T: PartialOrd + Copy> Pair<T> {
    pub fn larger(&self) -> T {
        if self.a > self.b { self.a } else { self.b }
    }
}

/// Drill 4: `Wrapper { value: 5 }.get()` is `&5`
impl<T> Wrapper<T> {
    pub fn get(&self) -> &T {
        &self.value
    }
}

/// Drill 5: `first(&[4, 5])` is `Some(4)`; an empty slice gives `None`
pub fn first<T: Copy>(items: &[T]) -> Option<T> {
    if items.is_empty() {
        None
    } else {
        Some(items[0])
    }
}

/// Drill 6: `shorter("hi", "hello")` is `"hi"`; on a tie, the first
pub fn shorter<'a>(a: &'a str, b: &'a str) -> &'a str {
    if b.len() < a.len() { b } else { a }
}

/// Drill 7: `before_comma("red, green")` is `"red"`; no comma gives all the text
pub fn before_comma(text: &str) -> &str {
    match text.find(',') {
        Some(i) => &text[..i],
        None => text,
    }
}

/// Drill 8: `through_colon("key: value")` is `"key:"`, the colon included
pub fn through_colon(text: &str) -> &str {
    match text.find(':') {
        Some(i) => &text[..=i],
        None => text,
    }
}
