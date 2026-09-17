use borrowing::*;

#[test]
fn first_word_of_sentence() {
    assert_eq!(first_word("hello brave new world"), "hello");
}

#[test]
fn first_word_single_and_empty() {
    assert_eq!(first_word("rust"), "rust");
    assert_eq!(first_word(""), "");
}

#[test]
fn first_word_is_a_slice_of_the_input() {
    let text = String::from("borrowed slice");
    let word = first_word(&text);
    assert_eq!(word.as_ptr(), text.as_ptr(), "return a slice of s, not a new String");
}

#[test]
fn first_word_handles_multibyte() {
    assert_eq!(first_word("héllo wörld"), "héllo");
}

#[test]
fn sums_slices() {
    assert_eq!(sum(&[1, 2, 3]), 6);
    assert_eq!(sum(&[]), 0);
    let v = vec![10, -5, 7];
    assert_eq!(sum(&v[1..]), 2);
}

#[test]
fn doubles_in_place() {
    let mut v = vec![1, -2, 3];
    double_all(&mut v);
    assert_eq!(v, [2, -4, 6]);
}

#[test]
fn appends_lines() {
    let mut buf = String::new();
    append_greeting(&mut buf, "Ana");
    append_greeting(&mut buf, "Budi");
    assert_eq!(buf, "Hello, Ana\nHello, Budi\n");
}
