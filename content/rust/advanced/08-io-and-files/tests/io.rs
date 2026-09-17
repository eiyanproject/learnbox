use std::fs;
use std::io::{self, BufReader};
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};

use io_and_files::*;

fn temp_path(name: &str) -> PathBuf {
    static N: AtomicUsize = AtomicUsize::new(0);
    let dir = std::env::temp_dir().join(format!("learnbox-io-{}-{}", std::process::id(), N.fetch_add(1, Ordering::SeqCst)));
    fs::create_dir_all(&dir).unwrap();
    dir.join(name)
}

#[test]
fn counts_from_memory() {
    assert_eq!(count_lines_and_words("one two\n\nthree  four five\n".as_bytes()).unwrap(), (3, 5));
    assert_eq!(count_lines_and_words("".as_bytes()).unwrap(), (0, 0));
    assert_eq!(count_lines_and_words("no newline".as_bytes()).unwrap(), (1, 2));
}

#[test]
fn counts_from_a_file() {
    let p = temp_path("words.txt");
    fs::write(&p, "a b\nc\n").unwrap();
    let reader = BufReader::new(fs::File::open(&p).unwrap());
    assert_eq!(count_lines_and_words(reader).unwrap(), (2, 3));
}

#[test]
fn report_into_a_vec() {
    let mut out = Vec::new();
    write_report(&mut out, &[("apples", 12), ("kiwi", 3)]).unwrap();
    assert_eq!(String::from_utf8(out).unwrap(), "apples       12\nkiwi          3\n");
}

#[test]
fn sums_a_csv_column() {
    let p = temp_path("scores.csv");
    fs::write(&p, "name,score,bonus\nana,90,1.5\nbudi,75,0\n\ncitra,82.5,2\n").unwrap();
    assert_eq!(sum_column(&p, 1).unwrap(), 247.5);
    assert_eq!(sum_column(&p, 2).unwrap(), 3.5);
}

#[test]
fn bad_csv_value_is_invalid_data() {
    let p = temp_path("bad.csv");
    fs::write(&p, "name,score\nana,90\nbudi,lots\n").unwrap();
    let err = sum_column(&p, 1).unwrap_err();
    assert_eq!(err.kind(), io::ErrorKind::InvalidData);
    assert!(err.to_string().contains("line 3"), "{err}");
}

#[test]
fn missing_file_is_not_found() {
    assert_eq!(sum_column(temp_path("nope.csv"), 0).unwrap_err().kind(), io::ErrorKind::NotFound);
}

#[test]
fn appends() {
    let p = temp_path("app.log");
    append_log(&p, "started").unwrap();
    append_log(&p, "stopped").unwrap();
    assert_eq!(fs::read_to_string(&p).unwrap(), "started\nstopped\n");
}

#[test]
fn copies_upper_case_in_chunks() {
    let src = temp_path("in.txt");
    let dst = temp_path("out.txt");
    let text = "stream me, please. ".repeat(2000);
    fs::write(&src, &text).unwrap();
    assert_eq!(copy_upper(&src, &dst).unwrap(), text.len());
    assert_eq!(fs::read_to_string(&dst).unwrap(), text.to_uppercase());
}
