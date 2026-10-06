#[derive(Debug, PartialEq, Eq)]
pub enum ParseError {
    Empty,
    MissingNumber,
    MissingUnit,
    UnknownUnit(char),
    Repeated(char),
}

const UNITS: [(char, u64); 4] = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)];

pub fn parse_duration(text: &str) -> Result<u64, ParseError> {
    if text.is_empty() {
        return Err(ParseError::Empty);
    }
    let mut total = 0;
    let mut number: Option<u64> = None;
    let mut seen: Vec<char> = Vec::new();
    for c in text.chars() {
        if let Some(digit) = c.to_digit(10) {
            number = Some(number.unwrap_or(0) * 10 + u64::from(digit));
            continue;
        }
        let Some(&(_, size)) = UNITS.iter().find(|(unit, _)| *unit == c) else {
            return Err(ParseError::UnknownUnit(c));
        };
        let count = number.take().ok_or(ParseError::MissingNumber)?;
        if seen.contains(&c) {
            return Err(ParseError::Repeated(c));
        }
        seen.push(c);
        total += count * size;
    }
    match number {
        Some(_) => Err(ParseError::MissingUnit),
        None => Ok(total),
    }
}

pub fn format_duration(mut seconds: u64) -> String {
    if seconds == 0 {
        return "0s".to_string();
    }
    let mut out = String::new();
    for (unit, size) in UNITS {
        let count = seconds / size;
        seconds %= size;
        if count > 0 {
            out.push_str(&format!("{count}{unit}"));
        }
    }
    out
}
