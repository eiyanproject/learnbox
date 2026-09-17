use std::fmt;
use std::time::Duration;

#[derive(Debug, PartialEq)]
#[must_use]
pub enum BuildError {
    MissingUrl,
    TooManyRetries(u8),
}

impl fmt::Display for BuildError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            BuildError::MissingUrl => write!(f, "a base URL is required"),
            BuildError::TooManyRetries(n) => write!(f, "{n} retries is more than the maximum of 10"),
        }
    }
}

impl std::error::Error for BuildError {}

#[derive(Debug, Clone, PartialEq)]
pub struct Client {
    url: String,
    timeout: Duration,
    retries: u8,
    headers: Vec<(String, String)>,
}

#[derive(Debug, Clone)]
#[must_use = "a ClientBuilder does nothing until you call build()"]
pub struct ClientBuilder {
    url: String,
    timeout: Duration,
    retries: u8,
    headers: Vec<(String, String)>,
}

impl Client {
    pub fn builder(url: impl Into<String>) -> ClientBuilder {
        ClientBuilder { url: url.into(), timeout: Duration::from_secs(30), retries: 0, headers: Vec::new() }
    }

    pub fn url(&self) -> &str {
        &self.url
    }

    pub fn timeout(&self) -> Duration {
        self.timeout
    }

    pub fn retries(&self) -> u8 {
        self.retries
    }

    pub fn configure(&mut self, timeout: Timeout, retries: Retries) {
        self.timeout = timeout.0;
        self.retries = retries.0;
    }

    #[must_use = "a RequestBuilder does nothing until you call send()"]
    pub fn request(&self, method: impl Into<String>, path: impl AsRef<str>) -> RequestBuilder {
        RequestBuilder {
            method: method.into(),
            url: format!("{}{}", self.url.trim_end_matches('/'), path.as_ref()),
            headers: self.headers.clone(),
        }
    }
}

impl ClientBuilder {
    pub fn timeout(mut self, timeout: Duration) -> Self {
        self.timeout = timeout;
        self
    }

    pub fn retries(mut self, retries: u8) -> Self {
        self.retries = retries;
        self
    }

    pub fn header(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.headers.push((key.into(), value.into()));
        self
    }

    pub fn build(self) -> Result<Client, BuildError> {
        if self.url.trim().is_empty() {
            return Err(BuildError::MissingUrl);
        }
        if self.retries > 10 {
            return Err(BuildError::TooManyRetries(self.retries));
        }
        Ok(Client { url: self.url, timeout: self.timeout, retries: self.retries, headers: self.headers })
    }
}

#[derive(Debug, Clone)]
#[must_use = "a RequestBuilder does nothing until you call send()"]
pub struct RequestBuilder {
    method: String,
    url: String,
    headers: Vec<(String, String)>,
}

impl RequestBuilder {
    pub fn header(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.headers.push((key.into(), value.into()));
        self
    }

    pub fn send(self) -> String {
        let headers: Vec<String> = self.headers.iter().map(|(k, v)| format!("{k}: {v}")).collect();
        format!("{} {} [{}]", self.method, self.url, headers.join(", "))
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Timeout(pub Duration);

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Retries(pub u8);

mod private {
    pub trait Sealed {}
}

/// Storage backends. Sealed: only this crate can add implementations.
pub trait Backend: private::Sealed {
    fn name(&self) -> &str;
    fn persistent(&self) -> bool;

    fn describe(&self) -> String {
        let kind = if self.persistent() { "persistent" } else { "volatile" };
        format!("{} ({kind})", self.name())
    }
}

#[derive(Debug, Default)]
pub struct Memory;

#[derive(Debug, Default)]
pub struct Disk {
    pub path: String,
}

impl private::Sealed for Memory {}
impl private::Sealed for Disk {}

impl Backend for Memory {
    fn name(&self) -> &str {
        "memory"
    }
    fn persistent(&self) -> bool {
        false
    }
}

impl Backend for Disk {
    fn name(&self) -> &str {
        "disk"
    }
    fn persistent(&self) -> bool {
        true
    }
}
