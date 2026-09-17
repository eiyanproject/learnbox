use std::borrow::Cow;

pub fn char_count(s: &str) -> usize {
    s.chars().count()
}

pub fn truncate_chars(s: &str, n: usize) -> &str {
    match s.char_indices().nth(n) {
        Some((byte_index, _)) => &s[..byte_index],
        None => s,
    }
}

pub fn capitalize_words(s: &str) -> String {
    s.split(' ')
        .map(|word| {
            let mut chars = word.chars();
            match chars.next() {
                Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
                None => String::new(),
            }
        })
        .collect::<Vec<_>>()
        .join(" ")
}

pub fn parse_rgb(s: &str) -> Option<(u8, u8, u8)> {
    let hex = s.strip_prefix('#')?;
    if hex.len() != 6 || !hex.is_ascii() {
        return None;
    }
    let channel = |range: std::ops::Range<usize>| u8::from_str_radix(&hex[range], 16).ok();
    Some((channel(0..2)?, channel(2..4)?, channel(4..6)?))
}

pub fn normalize_spaces(s: &str) -> Cow<'_, str> {
    if !s.contains("  ") {
        return Cow::Borrowed(s);
    }
    Cow::Owned(s.split(' ').filter(|w| !w.is_empty()).collect::<Vec<_>>().join(" "))
}
