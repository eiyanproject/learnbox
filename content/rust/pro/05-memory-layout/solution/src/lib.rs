use std::borrow::Cow;

/// 24 bytes because of padding.
#[repr(C)]
pub struct Wasteful {
    pub a: u8,
    pub b: u64,
    pub c: u16,
    pub d: u32,
}

/// Largest first: no padding is needed between the fields.
#[repr(C)]
pub struct Packed {
    pub b: u64,
    pub d: u32,
    pub c: u16,
    pub a: u8,
}

impl Packed {
    pub fn new(a: u8, b: u64, c: u16, d: u32) -> Self {
        Packed { b, d, c, a }
    }
}

pub fn sum_digits(s: &str) -> u64 {
    s.bytes().filter(u8::is_ascii_digit).map(|b| (b - b'0') as u64).sum()
}

pub fn join_with_capacity(parts: &[&str], sep: &str) -> String {
    if parts.is_empty() {
        return String::new();
    }
    let total = parts.iter().map(|p| p.len()).sum::<usize>() + sep.len() * (parts.len() - 1);
    let mut out = String::with_capacity(total);
    for (i, part) in parts.iter().enumerate() {
        if i > 0 {
            out.push_str(sep);
        }
        out.push_str(part);
    }
    out
}

pub fn normalize(s: &str) -> Cow<'_, str> {
    let trimmed = s.trim();
    if trimmed.bytes().any(|b| b.is_ascii_uppercase()) {
        Cow::Owned(trimmed.to_lowercase())
    } else {
        Cow::Borrowed(trimmed)
    }
}

pub fn count_words_reusing_buffer(lines: &[&str]) -> Vec<usize> {
    let mut buffer = String::new();
    let mut counts = Vec::with_capacity(lines.len());
    for line in lines {
        buffer.clear();
        buffer.push_str(line.trim());
        counts.push(buffer.split_whitespace().count());
    }
    counts
}
