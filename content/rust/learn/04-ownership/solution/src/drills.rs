// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, then press that drill's Run button in the
// Results tab: it builds and tests just that drill, so a mistake in one never
// stops the others. Keep the `/// Drill N:` lines; they mark where each drill
// starts. The hidden tests read this file directly, so it needs no `mod` line.

/// Drill 1: `make_greeting()` is the `String` `"hello"`
pub fn make_greeting() -> String {
    String::from("hello")
}

/// Drill 2: `add_question_mark("why")` is `"why?"`
pub fn add_question_mark(mut s: String) -> String {
    s.push('?');
    s
}

/// Drill 3: `copy_of(&s)` is a new `String` equal to `s`
pub fn copy_of(s: &String) -> String {
    s.clone()
}

/// Drill 4: `first_copy(&names)` is a copy of the first name, leaving `names` as it was
pub fn first_copy(names: &Vec<String>) -> String {
    names[0].clone()
}

/// Drill 5: `take_first(names)` moves the first name out and returns it
pub fn take_first(mut names: Vec<String>) -> String {
    names.remove(0)
}

/// Drill 6: `total_length(&words)` is the sum of the words' lengths: `["ab", "cde"]` gives `5`
pub fn total_length(words: &Vec<String>) -> usize {
    let mut total = 0;
    for w in words {
        total += w.len();
    }
    total
}

/// Drill 7: `count_then_keep(words)` is `(how many, the same words)`
pub fn count_then_keep(words: Vec<String>) -> (usize, Vec<String>) {
    let n = words.len();
    (n, words)
}

/// Drill 8: `both_ways(s)` is `(s, s)`: two separate `String`s
pub fn both_ways(s: String) -> (String, String) {
    let copy = s.clone();
    (copy, s)
}
