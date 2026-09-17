use std::fmt;
use std::time::Duration;

#[derive(Debug, PartialEq)]
pub enum BuildError {
    MissingUrl,
    TooManyRetries(u8),
}

#[derive(Debug, Clone)]
pub struct Client {
    // url, timeout, retries, headers
}

pub struct ClientBuilder {
    // the same fields, optional
}

impl Client {
    pub fn builder(url: impl Into<String>) -> ClientBuilder {
        todo!()
    }
}

// RequestBuilder with #[must_use], Timeout and Retries newtypes,
// and the sealed Backend trait with Memory and Disk.
