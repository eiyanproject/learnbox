// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, press Check, and that drill gets its own
// tick in the Results tab. The hidden tests read this file directly, so it
// needs no `mod` line anywhere.

/// Drill 1: `plus_one(4)` is `5`
pub fn plus_one(n: i32) -> i32 {
    n + 1
}

/// Drill 2: `area(3, 4)` is `12`
pub fn area(width: i32, height: i32) -> i32 {
    width * height
}

/// Drill 3: `hello()` is the `String` `"hello"`
pub fn hello() -> String {
    "hello".to_string()
}

/// Drill 4: `shout("hi")` is `"hi!"`
pub fn shout(word: &str) -> String {
    format!("{word}!")
}

/// Drill 5: `full_name("Ada", "Lovelace")` is `"Ada Lovelace"`
pub fn full_name(first: &str, last: &str) -> String {
    format!("{first} {last}")
}

/// Drill 6: `score_line("Ana", 92)` is `"Ana:    92"`: the score right-aligned in 5 characters
pub fn score_line(name: &str, score: i32) -> String {
    format!("{name}: {score:>5}")
}

/// Drill 7: `letters("cargo")` is `5`
pub fn letters(word: &str) -> usize {
    word.len()
}

/// Drill 8: `stars(3)` is `"***"`
pub fn stars(n: usize) -> String {
    "*".repeat(n)
}

/// Drill 9: `two_lines("a", "b")` is `"a\nb"`: `a`, a line break, `b`
pub fn two_lines(top: &str, bottom: &str) -> String {
    format!("{top}\n{bottom}")
}

/// Drill 10: `underline("hi")` is `"hi\n--"`: the word, then a line of `-` as long as it
pub fn underline(word: &str) -> String {
    let line = "-".repeat(word.len());
    format!("{word}\n{line}")
}
