use std::collections::HashMap;
use std::error::Error;

use error_design::*;

fn cfg(pairs: &[(&str, &str)]) -> HashMap<String, String> {
    pairs.iter().map(|(k, v)| (k.to_string(), v.to_string())).collect()
}

#[test]
fn port_ok() {
    assert_eq!(get_port(&cfg(&[("port", " 8080 ")])).unwrap(), 8080);
    assert_eq!(get_port(&cfg(&[("port", "65535")])).unwrap(), 65535);
}

#[test]
fn port_missing() {
    let err = get_port(&cfg(&[])).unwrap_err();
    assert!(matches!(&err, ConfigError::Missing(k) if k == "port"));
    assert_eq!(err.to_string(), "missing key: port");
    assert!(err.source().is_none());
}

#[test]
fn port_not_a_number_keeps_source() {
    let err = get_port(&cfg(&[("port", "http")])).unwrap_err();
    assert!(matches!(&err, ConfigError::InvalidNumber { key, .. } if key == "port"));
    assert_eq!(err.to_string(), "port is not a number");
    let source = err.source().expect("InvalidNumber must expose its source");
    assert_eq!(source.to_string(), "invalid digit found in string");
}

#[test]
fn port_out_of_range() {
    for (raw, value) in [("0", 0), ("70000", 70000), ("-1", -1)] {
        let err = get_port(&cfg(&[("port", raw)])).unwrap_err();
        assert!(matches!(&err, ConfigError::OutOfRange { value: v, .. } if *v == value));
    }
    assert_eq!(get_port(&cfg(&[("port", "70000")])).unwrap_err().to_string(), "port out of range: 70000");
}

#[test]
fn workers_default_and_range() {
    assert_eq!(get_workers(&cfg(&[])).unwrap(), 4);
    assert_eq!(get_workers(&cfg(&[("workers", "16")])).unwrap(), 16);
    assert_eq!(get_workers(&cfg(&[("workers", "65")])).unwrap_err().to_string(), "workers out of range: 65");
}

#[test]
fn load_boxes_errors() {
    assert_eq!(load(&cfg(&[("port", "80"), ("workers", "2")])).unwrap(), (80, 2));
    let err: Box<dyn Error> = load(&cfg(&[("port", "80"), ("workers", "x")])).unwrap_err();
    assert_eq!(err.to_string(), "workers is not a number");
    assert!(err.downcast_ref::<ConfigError>().is_some());
}
