use std::borrow::Cow;

use zero_copy::*;

const LOG: &str = "\
2026-09-18T01:20:56Z INFO web: started on :8080
2026-09-18T01:21:02Z ERROR db: connection lost: timeout after 30s
not a log line
2026-09-18T01:21:05Z WARN cache: 90% full
2026-09-18T01:21:09Z ERROR web: upstream 503
";

#[test]
fn parses_one_line() {
    let e = parse_line("2026-09-18T01:20:56Z ERROR db: connection lost").unwrap();
    assert_eq!(e.timestamp, "2026-09-18T01:20:56Z");
    assert_eq!(e.level, "ERROR");
    assert_eq!(e.target, "db");
    assert_eq!(e.message, "connection lost");
}

#[test]
fn message_keeps_spaces_and_colons() {
    let e = parse_line("t L target: a: b c").unwrap();
    assert_eq!(e.message, "a: b c");
}

#[test]
fn rejects_malformed() {
    for bad in ["", "only-one-field", "ts LEVEL no-colon", "ts LEVEL two words: x"] {
        assert!(parse_line(bad).is_none(), "{bad:?}");
    }
}

#[test]
fn fields_borrow_from_the_input() {
    let line = String::from("ts LEVEL target: message");
    let e = parse_line(&line).unwrap();
    assert_eq!(e.timestamp.as_ptr(), line.as_ptr(), "parse without allocating");
}

#[test]
fn filters_errors() {
    let errors = errors_only(LOG);
    assert_eq!(errors.len(), 2);
    assert_eq!(errors[0].target, "db");
    assert_eq!(errors[0].message, "connection lost: timeout after 30s");
    assert_eq!(errors[1].message, "upstream 503");
}

#[test]
fn query_borrows_plain_values() {
    let pairs = parse_query("a=1&b=plain&c=");
    assert_eq!(pairs.len(), 3);
    assert!(matches!(pairs[0], ("a", Cow::Borrowed("1"))));
    assert!(matches!(pairs[1], ("b", Cow::Borrowed("plain"))));
    assert_eq!(pairs[2].1, "");
}

#[test]
fn query_decodes_when_needed() {
    let pairs = parse_query("q=hello+world&path=%2Fusr%2Fbin&flag");
    assert!(matches!(pairs[0].1, Cow::Owned(_)));
    assert_eq!(pairs[0].1, "hello world");
    assert_eq!(pairs[1].1, "/usr/bin");
    assert_eq!(pairs[2], ("flag", Cow::Borrowed("")));
}

#[test]
fn csv_rows_and_columns() {
    let text = "name, score\nana, 90\nbudi, 75\n";
    let csv = Csv::new(text, ',');
    assert_eq!(csv.rows().collect::<Vec<_>>(), [vec!["name", "score"], vec!["ana", "90"], vec!["budi", "75"]]);
    assert_eq!(csv.column("score"), ["90", "75"]);
    assert_eq!(csv.column("missing"), Vec::<&str>::new());
    assert!(Csv::new("", ',').column("x").is_empty());
}

#[test]
fn csv_values_point_into_the_text() {
    let text = String::from("a,b\nc,d\n");
    let csv = Csv::new(&text, ',');
    let first = csv.rows().next().unwrap()[0];
    assert_eq!(first.as_ptr(), text.as_ptr());
}

#[test]
fn longest() {
    assert_eq!(longest_field("a,bbb\ncc,d", ','), "bbb");
    assert_eq!(longest_field("", ','), "");
}
