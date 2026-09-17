use std::borrow::Cow;

use strings_and_text::*;

#[test]
fn counts_chars_not_bytes() {
    assert_eq!(char_count("hello"), 5);
    assert_eq!(char_count("héllo"), 5);
    assert_eq!(char_count("日本語"), 3);
    assert_eq!(char_count(""), 0);
}

#[test]
fn truncates_on_char_boundaries() {
    assert_eq!(truncate_chars("héllo", 2), "hé");
    assert_eq!(truncate_chars("日本語テキスト", 3), "日本語");
    assert_eq!(truncate_chars("short", 10), "short");
    assert_eq!(truncate_chars("abc", 0), "");
}

#[test]
fn truncate_returns_a_slice() {
    let text = String::from("borrowed");
    assert_eq!(truncate_chars(&text, 3).as_ptr(), text.as_ptr());
}

#[test]
fn capitalizes() {
    assert_eq!(capitalize_words("hello brave world"), "Hello Brave World");
    assert_eq!(capitalize_words("élan vital"), "Élan Vital");
    assert_eq!(capitalize_words("ßtraße"), "SStraße");
    assert_eq!(capitalize_words("a  b"), "A  B");
}

#[test]
fn rgb() {
    assert_eq!(parse_rgb("#ff8000"), Some((255, 128, 0)));
    assert_eq!(parse_rgb("#000000"), Some((0, 0, 0)));
    assert_eq!(parse_rgb("#FFffFF"), Some((255, 255, 255)));
}

#[test]
fn rgb_rejects() {
    for bad in ["ff8000", "#ff800", "#ff80000", "#gg0000", "#ff80é", "", "#"] {
        assert_eq!(parse_rgb(bad), None, "{bad:?}");
    }
}

#[test]
fn normalize_borrows_when_clean() {
    assert!(matches!(normalize_spaces("already clean"), Cow::Borrowed("already clean")));
}

#[test]
fn normalize_collapses_runs() {
    let out = normalize_spaces("too   many  spaces");
    assert!(matches!(out, Cow::Owned(_)));
    assert_eq!(out, "too many spaces");
    assert_eq!(normalize_spaces("  padded  "), "padded");
}
