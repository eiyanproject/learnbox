#[derive(Debug, PartialEq, Eq)]
pub enum ParseError {
    Empty,
    MissingNumber,
    MissingUnit,
    UnknownUnit(char),
    Repeated(char),
}

pub fn parse_duration(text: &str) -> Result<u64, ParseError> {
    todo!()
}

pub fn format_duration(seconds: u64) -> String {
    todo!()
}
