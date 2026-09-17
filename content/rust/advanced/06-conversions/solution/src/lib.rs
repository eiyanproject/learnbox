use std::ops::Deref;
use std::str::FromStr;

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Port(pub u16);

#[derive(Debug, PartialEq)]
pub enum PortError {
    Zero,
}

impl TryFrom<u16> for Port {
    type Error = PortError;

    fn try_from(value: u16) -> Result<Self, PortError> {
        if value == 0 { Err(PortError::Zero) } else { Ok(Port(value)) }
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Rgb {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

#[derive(Debug, PartialEq)]
pub struct ParseRgbError;

impl FromStr for Rgb {
    type Err = ParseRgbError;

    fn from_str(s: &str) -> Result<Self, ParseRgbError> {
        let inner = s.trim().strip_prefix("rgb(").and_then(|r| r.strip_suffix(')')).ok_or(ParseRgbError)?;
        let parts: Vec<u8> = inner
            .split(',')
            .map(|p| p.trim().parse::<u8>().map_err(|_| ParseRgbError))
            .collect::<Result<_, _>>()?;
        match parts[..] {
            [r, g, b] => Ok(Rgb { r, g, b }),
            _ => Err(ParseRgbError),
        }
    }
}

impl From<Rgb> for String {
    fn from(c: Rgb) -> String {
        format!("#{:02x}{:02x}{:02x}", c.r, c.g, c.b)
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Celsius(pub f64);

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Fahrenheit(pub f64);

impl From<Celsius> for Fahrenheit {
    fn from(c: Celsius) -> Self {
        Fahrenheit(c.0 * 9.0 / 5.0 + 32.0)
    }
}

impl From<Fahrenheit> for Celsius {
    fn from(f: Fahrenheit) -> Self {
        Celsius((f.0 - 32.0) * 5.0 / 9.0)
    }
}

pub fn total_len<S: AsRef<str>>(items: &[S]) -> usize {
    items.iter().map(|s| s.as_ref().len()).sum()
}

pub struct NonEmptyVec<T>(Vec<T>);

impl<T> NonEmptyVec<T> {
    pub fn new(items: Vec<T>) -> Option<Self> {
        if items.is_empty() { None } else { Some(NonEmptyVec(items)) }
    }

    pub fn first(&self) -> &T {
        &self.0[0]
    }
}

impl<T> Deref for NonEmptyVec<T> {
    type Target = [T];

    fn deref(&self) -> &[T] {
        &self.0
    }
}
