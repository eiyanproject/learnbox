use std::borrow::Cow;

pub fn char_count(s: &str) -> usize {
    s.len() // bytes, not characters
}

pub fn truncate_chars(s: &str, n: usize) -> &str {
    &s[..n.min(s.len())] // can split a multi-byte character
}

pub fn capitalize_words(s: &str) -> String {
    todo!()
}

pub fn parse_rgb(s: &str) -> Option<(u8, u8, u8)> {
    todo!()
}

pub fn normalize_spaces(s: &str) -> Cow<'_, str> {
    todo!()
}
