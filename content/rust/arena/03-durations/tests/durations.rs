use arena_durations::*;

#[test]
fn single_units() {
    assert_eq!(parse_duration("90s"), Ok(90));
    assert_eq!(parse_duration("5m"), Ok(300));
    assert_eq!(parse_duration("2h"), Ok(7200));
    assert_eq!(parse_duration("1d"), Ok(86400));
}

#[test]
fn several_parts_add_up() {
    assert_eq!(parse_duration("1h30m"), Ok(5400));
    assert_eq!(parse_duration("2d5s"), Ok(172805));
    assert_eq!(parse_duration("1d1h1m1s"), Ok(90061));
}

#[test]
fn any_order() {
    assert_eq!(parse_duration("30m1h"), Ok(5400));
    assert_eq!(parse_duration("5s2d"), Ok(172805));
}

#[test]
fn zero_and_big_numbers() {
    assert_eq!(parse_duration("0s"), Ok(0));
    assert_eq!(parse_duration("0h0m"), Ok(0));
    assert_eq!(parse_duration("120m"), Ok(7200));
    assert_eq!(parse_duration("007s"), Ok(7));
}

#[test]
fn empty() {
    assert_eq!(parse_duration(""), Err(ParseError::Empty));
}

#[test]
fn a_unit_needs_a_number() {
    assert_eq!(parse_duration("h"), Err(ParseError::MissingNumber));
    assert_eq!(parse_duration("5mm"), Err(ParseError::MissingNumber));
    assert_eq!(parse_duration("1hm"), Err(ParseError::MissingNumber));
}

#[test]
fn a_number_needs_a_unit() {
    assert_eq!(parse_duration("5"), Err(ParseError::MissingUnit));
    assert_eq!(parse_duration("1h30"), Err(ParseError::MissingUnit));
}

#[test]
fn unknown_characters_are_named() {
    assert_eq!(parse_duration("5x"), Err(ParseError::UnknownUnit('x')));
    assert_eq!(parse_duration("1h 30m"), Err(ParseError::UnknownUnit(' ')));
    assert_eq!(parse_duration("5H"), Err(ParseError::UnknownUnit('H')));
    assert_eq!(parse_duration("-5s"), Err(ParseError::UnknownUnit('-')));
    assert_eq!(parse_duration("1.5h"), Err(ParseError::UnknownUnit('.')));
}

#[test]
fn a_unit_may_appear_once() {
    assert_eq!(parse_duration("1h2h"), Err(ParseError::Repeated('h')));
    assert_eq!(parse_duration("1s2m3s"), Err(ParseError::Repeated('s')));
}

#[test]
fn the_first_problem_wins() {
    assert_eq!(parse_duration("x5"), Err(ParseError::UnknownUnit('x')));
    assert_eq!(parse_duration("h5"), Err(ParseError::MissingNumber));
    assert_eq!(parse_duration("1h1h5"), Err(ParseError::Repeated('h')));
    assert_eq!(parse_duration("1h?5"), Err(ParseError::UnknownUnit('?')));
}

#[test]
fn formats_largest_first_and_skips_zeros() {
    assert_eq!(format_duration(5400), "1h30m");
    assert_eq!(format_duration(172805), "2d5s");
    assert_eq!(format_duration(90061), "1d1h1m1s");
    assert_eq!(format_duration(59), "59s");
    assert_eq!(format_duration(60), "1m");
    assert_eq!(format_duration(86400 * 400), "400d");
}

#[test]
fn zero_is_zero_seconds() {
    assert_eq!(format_duration(0), "0s");
}

#[test]
fn round_trip() {
    for n in [0, 1, 59, 60, 61, 3599, 3600, 86399, 86400, 123_456_789] {
        assert_eq!(parse_duration(&format_duration(n)), Ok(n), "round trip of {n}");
    }
}
