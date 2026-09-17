use std::borrow::Cow;

/// 24 bytes because of padding.
#[repr(C)]
pub struct Wasteful {
    pub a: u8,
    pub b: u64,
    pub c: u16,
    pub d: u32,
}

/// Reorder these fields so the struct is 16 bytes.
#[repr(C)]
pub struct Packed {
    pub a: u8,
    pub b: u64,
    pub c: u16,
    pub d: u32,
}

impl Packed {
    pub fn new(a: u8, b: u64, c: u16, d: u32) -> Self {
        Packed { a, b, c, d }
    }
}

pub fn sum_digits(s: &str) -> u64 {
    // This allocates a Vec and a String for every call.
    let digits: Vec<char> = s.chars().filter(|c| c.is_ascii_digit()).collect();
    digits.iter().collect::<String>().chars().map(|c| c.to_digit(10).unwrap() as u64).sum()
}

pub fn join_with_capacity(parts: &[&str], sep: &str) -> String {
    todo!()
}

pub fn normalize(s: &str) -> Cow<'_, str> {
    todo!()
}

pub fn count_words_reusing_buffer(lines: &[&str]) -> Vec<usize> {
    todo!()
}
