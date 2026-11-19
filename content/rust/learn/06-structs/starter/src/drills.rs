// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, then press that drill's Run button in the
// Results tab: it builds and tests just that drill, so a mistake in one never
// stops the others. Keep the `/// Drill N:` lines; they mark where each drill
// starts. The hidden tests read this file directly, so it needs no `mod` line.

/// The point the drills below work on. Already written: read it first.
#[derive(Debug, Clone, PartialEq)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

/// Drill 1: `origin()` is the point `(0, 0)`
pub fn origin() -> Point {
    todo!()
}

/// Drill 2: `point(3, 4)` is `Point { x: 3, y: 4 }`
pub fn point(x: i32, y: i32) -> Point {
    todo!()
}

/// Drill 3: `sum_of(&p)` is `p.x + p.y`
pub fn sum_of(p: &Point) -> i32 {
    todo!()
}

/// Drill 4: `move_right(&mut p)` adds 1 to `p.x`
pub fn move_right(p: &mut Point) {
    todo!()
}

/// Drill 5: `Point::new(1, 2)` builds a point
impl Point {
    pub fn new(x: i32, y: i32) -> Self {
        todo!()
    }
}

/// Drill 6: `p.distance()` is `|x| + |y|`: `Point { x: -3, y: 4 }.distance()` is `7`
impl Point {
    pub fn distance(&self) -> i32 {
        todo!()
    }
}

/// Drill 7: `p.shift(2, -1)` moves the point by that much
impl Point {
    pub fn shift(&mut self, dx: i32, dy: i32) {
        todo!()
    }
}

/// Drill 8: `p.into_pair()` is `(x, y)`; it uses up the point
impl Point {
    pub fn into_pair(self) -> (i32, i32) {
        todo!()
    }
}

/// Drill 9: `debug_text(&p)` is `"Point { x: 1, y: 2 }"`
pub fn debug_text(p: &Point) -> String {
    todo!()
}
