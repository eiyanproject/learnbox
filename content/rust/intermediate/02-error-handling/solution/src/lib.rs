use std::collections::HashMap;
use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
pub enum ConfigError {
    Missing(String),
    InvalidNumber { key: String, source: ParseIntError },
    OutOfRange { key: String, value: i64 },
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            ConfigError::Missing(key) => write!(f, "missing key: {key}"),
            ConfigError::InvalidNumber { key, .. } => write!(f, "{key} is not a number"),
            ConfigError::OutOfRange { key, value } => write!(f, "{key} out of range: {value}"),
        }
    }
}

impl Error for ConfigError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            ConfigError::InvalidNumber { source, .. } => Some(source),
            _ => None,
        }
    }
}

fn parse_in_range(key: &str, raw: &str, min: i64, max: i64) -> Result<u16, ConfigError> {
    let value = raw
        .trim()
        .parse::<i64>()
        .map_err(|source| ConfigError::InvalidNumber { key: key.to_string(), source })?;
    if value < min || value > max {
        return Err(ConfigError::OutOfRange { key: key.to_string(), value });
    }
    Ok(value as u16)
}

pub fn get_port(config: &HashMap<String, String>) -> Result<u16, ConfigError> {
    let raw = config.get("port").ok_or_else(|| ConfigError::Missing("port".to_string()))?;
    parse_in_range("port", raw, 1, 65535)
}

pub fn get_workers(config: &HashMap<String, String>) -> Result<u16, ConfigError> {
    match config.get("workers") {
        None => Ok(4),
        Some(raw) => parse_in_range("workers", raw, 1, 64),
    }
}

pub fn load(config: &HashMap<String, String>) -> Result<(u16, u16), Box<dyn Error>> {
    Ok((get_port(config)?, get_workers(config)?))
}
