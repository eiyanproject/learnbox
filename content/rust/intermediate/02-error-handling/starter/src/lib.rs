use std::collections::HashMap;
use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
pub enum ConfigError {
    // Add the variants.
}

// impl fmt::Display for ConfigError { ... }

// impl Error for ConfigError { ... }

pub fn get_port(config: &HashMap<String, String>) -> Result<u16, ConfigError> {
    todo!()
}

pub fn get_workers(config: &HashMap<String, String>) -> Result<u16, ConfigError> {
    todo!()
}

pub fn load(config: &HashMap<String, String>) -> Result<(u16, u16), Box<dyn Error>> {
    todo!()
}
