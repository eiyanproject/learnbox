use std::borrow::Cow;

#[derive(Debug, PartialEq)]
pub struct LogEntry<'a> {
    pub timestamp: &'a str,
    pub level: &'a str,
    pub target: &'a str,
    pub message: &'a str,
}

pub fn parse_line(line: &str) -> Option<LogEntry<'_>> {
    let line = line.trim_end();
    let (timestamp, rest) = line.split_once(' ')?;
    let (level, rest) = rest.split_once(' ')?;
    let (target, message) = rest.split_once(": ")?;
    if timestamp.is_empty() || level.is_empty() || target.is_empty() || target.contains(' ') {
        return None;
    }
    Some(LogEntry { timestamp, level, target, message })
}

pub fn errors_only(text: &str) -> Vec<LogEntry<'_>> {
    text.lines().filter_map(parse_line).filter(|e| e.level == "ERROR").collect()
}

fn decode(raw: &str) -> Cow<'_, str> {
    if !raw.contains('+') && !raw.contains('%') {
        return Cow::Borrowed(raw);
    }
    let bytes = raw.as_bytes();
    let mut out = String::with_capacity(raw.len());
    let mut i = 0;
    while i < bytes.len() {
        match bytes[i] {
            b'+' => {
                out.push(' ');
                i += 1;
            }
            b'%' if i + 2 < bytes.len() => match u8::from_str_radix(&raw[i + 1..i + 3], 16) {
                Ok(byte) => {
                    out.push(byte as char);
                    i += 3;
                }
                Err(_) => {
                    out.push('%');
                    i += 1;
                }
            },
            _ => {
                let ch = raw[i..].chars().next().unwrap();
                out.push(ch);
                i += ch.len_utf8();
            }
        }
    }
    Cow::Owned(out)
}

pub fn parse_query(query: &str) -> Vec<(&str, Cow<'_, str>)> {
    query
        .split('&')
        .filter(|pair| !pair.is_empty())
        .map(|pair| match pair.split_once('=') {
            Some((key, value)) => (key, decode(value)),
            None => (pair, Cow::Borrowed("")),
        })
        .collect()
}

pub struct Csv<'a> {
    text: &'a str,
    sep: char,
}

impl<'a> Csv<'a> {
    pub fn new(text: &'a str, sep: char) -> Self {
        Csv { text, sep }
    }

    pub fn rows(&self) -> impl Iterator<Item = Vec<&'a str>> + '_ {
        let sep = self.sep;
        self.text.lines().filter(|l| !l.is_empty()).map(move |line| line.split(sep).map(str::trim).collect())
    }

    pub fn column(&self, name: &str) -> Vec<&'a str> {
        let mut rows = self.rows();
        let Some(header) = rows.next() else {
            return Vec::new();
        };
        let Some(index) = header.iter().position(|h| *h == name) else {
            return Vec::new();
        };
        rows.filter_map(|row| row.get(index).copied()).collect()
    }
}

pub fn longest_field(text: &str, sep: char) -> &str {
    text.lines()
        .flat_map(|line| line.split(sep))
        .map(str::trim)
        .max_by_key(|field| field.len())
        .unwrap_or("")
}
