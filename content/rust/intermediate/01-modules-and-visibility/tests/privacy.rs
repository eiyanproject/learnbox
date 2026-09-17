// Compile-time checks that private things stay private are hard to express
// in an integration test, so this checks the source instead.
use std::fs;

#[test]
fn units_module_is_private() {
    let lib = fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    assert!(lib.lines().any(|l| l.trim() == "mod units;"), "declare `mod units;` without pub");
}

#[test]
fn round2_is_crate_visible() {
    let units = fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/units.rs")).unwrap();
    assert!(units.contains("pub(crate) fn round2"));
}

#[test]
fn radius_field_is_private() {
    let circle = fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/shapes/circle.rs")).unwrap();
    assert!(circle.contains("pub struct Circle"));
    assert!(!circle.contains("pub radius"), "keep the field private and expose radius()");
}
