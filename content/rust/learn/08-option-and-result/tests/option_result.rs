use option_and_result::*;

#[test]
fn find_index_present() {
    assert_eq!(find_index(&["a", "b", "c"], "c"), Some(2));
    assert_eq!(find_index(&["x", "x"], "x"), Some(0));
}

#[test]
fn find_index_missing() {
    assert_eq!(find_index(&["a", "b"], "z"), None);
    assert_eq!(find_index(&[], "a"), None);
}

#[test]
fn parse_age_ok() {
    assert_eq!(parse_age("42"), Ok(42));
    assert_eq!(parse_age(" 7\n"), Ok(7));
    assert_eq!(parse_age("0"), Ok(0));
    assert_eq!(parse_age("150"), Ok(150));
}

#[test]
fn parse_age_not_a_number() {
    assert_eq!(parse_age("forty"), Err("not a number: forty".to_string()));
    assert_eq!(parse_age("4.5"), Err("not a number: 4.5".to_string()));
}

#[test]
fn parse_age_out_of_range() {
    assert_eq!(parse_age("151"), Err("out of range: 151".to_string()));
    assert_eq!(parse_age("-3"), Err("out of range: -3".to_string()));
}

#[test]
fn add_strings_ok() {
    assert_eq!(add_strings("40", " 2"), Ok(42));
    assert_eq!(add_strings("-5", "5"), Ok(0));
}

#[test]
fn add_strings_passes_error_up() {
    let err = add_strings("1", "two").unwrap_err();
    assert_eq!(err, "two".parse::<i64>().unwrap_err());
    assert!(add_strings("x", "1").is_err());
}

#[test]
fn divide() {
    assert_eq!(safe_divide(7, 2), Some(3));
    assert_eq!(safe_divide(7, 0), None);
}
