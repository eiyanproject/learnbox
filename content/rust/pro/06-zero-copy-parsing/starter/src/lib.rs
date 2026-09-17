use std::borrow::Cow;

#[derive(Debug, PartialEq)]
pub struct LogEntry<'a> {
    pub timestamp: &'a str,
    pub level: &'a str,
    pub target: &'a str,
    pub message: &'a str,
}

pub fn parse_line(line: &str) -> Option<LogEntry<'_>> {
    todo!()
}

pub fn errors_only(text: &str) -> Vec<LogEntry<'_>> {
    todo!()
}

pub fn parse_query(query: &str) -> Vec<(&str, Cow<'_, str>)> {
    todo!()
}

pub struct Csv<'a> {
    text: &'a str,
    sep: char,
}

impl<'a> Csv<'a> {
    pub fn new(text: &'a str, sep: char) -> Self {
        Csv { text, sep }
    }

    // rows, column
}

pub fn longest_field(text: &str, sep: char) -> &str {
    todo!()
}
