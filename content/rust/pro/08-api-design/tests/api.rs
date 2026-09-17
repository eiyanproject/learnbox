use std::time::Duration;

use api_design::*;

#[test]
fn builder_defaults() {
    let c = Client::builder("https://api.example.com").build().unwrap();
    assert_eq!(c.url(), "https://api.example.com");
    assert_eq!(c.timeout(), Duration::from_secs(30));
    assert_eq!(c.retries(), 0);
}

#[test]
fn builder_accepts_str_and_string() {
    Client::builder(String::from("https://x")).build().unwrap();
    let c = Client::builder("https://x").timeout(Duration::from_secs(5)).retries(3).build().unwrap();
    assert_eq!((c.timeout(), c.retries()), (Duration::from_secs(5), 3));
}

#[test]
fn builder_validates() {
    assert_eq!(Client::builder("").build().unwrap_err(), BuildError::MissingUrl);
    assert_eq!(Client::builder("   ").build().unwrap_err(), BuildError::MissingUrl);
    assert_eq!(Client::builder("https://x").retries(11).build().unwrap_err(), BuildError::TooManyRetries(11));
    assert!(Client::builder("https://x").retries(10).build().is_ok());
}

#[test]
fn requests_inherit_client_headers() {
    let client = Client::builder("https://api.example.com/").header("Authorization", "Bearer t").build().unwrap();
    let sent = client.request("GET", "/users").header("Accept", "json").send();
    assert_eq!(sent, "GET https://api.example.com/users [Authorization: Bearer t, Accept: json]");
    assert_eq!(client.request("POST", "/x").send(), "POST https://api.example.com/x [Authorization: Bearer t]");
}

#[test]
fn newtypes_name_the_arguments() {
    let mut client = Client::builder("https://x").build().unwrap();
    client.configure(Timeout(Duration::from_millis(500)), Retries(2));
    assert_eq!((client.timeout(), client.retries()), (Duration::from_millis(500), 2));
}

#[test]
fn backends_share_a_default_method() {
    assert_eq!(Memory.describe(), "memory (volatile)");
    assert_eq!(Disk { path: "/data".into() }.describe(), "disk (persistent)");
    let backends: Vec<Box<dyn Backend>> = vec![Box::new(Memory), Box::new(Disk::default())];
    assert_eq!(backends.iter().map(|b| b.name()).collect::<Vec<_>>(), ["memory", "disk"]);
}

#[test]
fn api_uses_must_use_and_sealing() {
    let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    assert!(src.contains("#[must_use"), "mark types that do nothing until consumed");
    assert!(src.contains("Sealed"), "the Backend trait should be sealed");
    assert!(src.contains("impl Into<String>"), "accept both &str and String");
}
