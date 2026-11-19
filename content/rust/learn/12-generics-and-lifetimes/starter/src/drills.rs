// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, press Check, and that drill gets its own
// tick in the Results tab. The hidden tests read this file directly, so it
// needs no `mod` line anywhere.

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
        todo!()
    }
}

/// Drill 2: `Pair::new(1, 2).swap()` is `Pair { a: 2, b: 1 }`
impl<T> Pair<T> {
    pub fn swap(self) -> Pair<T> {
        todo!()
    }
}

/// Drill 3: `Pair::new(3, 9).larger()` is `9`
impl<T: PartialOrd + Copy> Pair<T> {
    pub fn larger(&self) -> T {
        todo!()
    }
}

/// Drill 4: `Wrapper { value: 5 }.get()` is `&5`
impl<T> Wrapper<T> {
    pub fn get(&self) -> &T {
        todo!()
    }
}

/// Drill 5: `first(&[4, 5])` is `Some(4)`; an empty slice gives `None`
pub fn first<T: Copy>(items: &[T]) -> Option<T> {
    todo!()
}

/// Drill 6: `shorter("hi", "hello")` is `"hi"`; on a tie, the first
pub fn shorter<'a>(a: &'a str, b: &'a str) -> &'a str {
    todo!()
}

/// Drill 7: `before_comma("red, green")` is `"red"`; no comma gives all the text
pub fn before_comma(text: &str) -> &str {
    todo!()
}

/// Drill 8: `through_colon("key: value")` is `"key:"`, the colon included
pub fn through_colon(text: &str) -> &str {
    todo!()
}
