// Practice drills. Each one is a small function that uses one thing from
// the lesson. Replace a `todo!()`, press Check, and that drill gets its own
// tick in the Results tab. The hidden tests read this file directly, so it
// needs no `mod` line anywhere.

/// Drill 1: `length(&s)` is the length of a borrowed `String`
pub fn length(s: &String) -> usize {
    s.len()
}

/// Drill 2: `add_one(&mut n)` adds one to the caller's `n`
pub fn add_one(n: &mut i32) {
    *n += 1;
}

/// Drill 3: `exclaim(&mut s)` adds `!` to the end of the caller's `String`
pub fn exclaim(s: &mut String) {
    s.push('!');
}

/// Drill 4: `first_three("rustacean")` is `"rus"`, a slice of the text
pub fn first_three(s: &str) -> &str {
    &s[0..3]
}

/// Drill 5: `after_first("xhello")` is `"hello"`
pub fn after_first(s: &str) -> &str {
    &s[1..]
}

/// Drill 6: `middle(&[1, 2, 3, 4])` is `[2, 3]`: all but the first and last
pub fn middle(v: &[i32]) -> &[i32] {
    &v[1..v.len() - 1]
}

/// Drill 7: `char_count("héllo")` is `5`, though it is 6 bytes
pub fn char_count(s: &str) -> usize {
    s.chars().count()
}

/// Drill 8: `space_at("hi there")` is `Some(2)`; no space gives `None`
pub fn space_at(s: &str) -> Option<usize> {
    s.find(' ')
}

/// Drill 9: `negate_all(&mut v)` turns `[1, -2]` into `[-1, 2]`, in place
pub fn negate_all(nums: &mut [i32]) {
    for n in nums.iter_mut() {
        *n = -*n;
    }
}

/// Drill 10: `add_line(&mut buf, "b")` turns `"a\n"` into `"a\nb\n"`
pub fn add_line(buf: &mut String, line: &str) {
    buf.push_str(line);
    buf.push('\n');
}
