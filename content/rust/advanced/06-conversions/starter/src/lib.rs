use std::ops::Deref;
use std::str::FromStr;

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Port(pub u16);

#[derive(Debug, PartialEq)]
pub enum PortError {
    Zero,
}

// impl TryFrom<u16> for Port

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Rgb {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

#[derive(Debug, PartialEq)]
pub struct ParseRgbError;

// impl FromStr for Rgb
// impl From<Rgb> for String

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Celsius(pub f64);

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Fahrenheit(pub f64);

// impl From<Celsius> for Fahrenheit, and back

pub fn total_len<S: AsRef<str>>(items: &[S]) -> usize {
    todo!()
}

pub struct NonEmptyVec<T>(Vec<T>);

impl<T> NonEmptyVec<T> {
    pub fn new(items: Vec<T>) -> Option<Self> {
        todo!()
    }
}
