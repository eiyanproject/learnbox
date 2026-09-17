use generics_and_lifetimes::*;

#[test]
fn longest_picks_longer() {
    assert_eq!(longest("hello", "hi"), "hello");
    assert_eq!(longest("a", "abc"), "abc");
}

#[test]
fn longest_prefers_first_on_tie() {
    let a = String::from("same");
    let b = String::from("size");
    assert_eq!(longest(&a, &b).as_ptr(), a.as_ptr());
}

#[test]
fn stack_of_numbers() {
    let mut s = Stack::new();
    assert!(s.is_empty());
    s.push(1);
    s.push(2);
    assert_eq!(s.len(), 2);
    assert_eq!(s.peek(), Some(&2));
    assert_eq!(s.pop(), Some(2));
    assert_eq!(s.pop(), Some(1));
    assert_eq!(s.pop(), None);
    assert!(s.is_empty());
}

#[test]
fn stack_of_strings() {
    let mut s: Stack<String> = Stack::new();
    s.push("a".to_string());
    assert_eq!(s.peek().map(|x| x.as_str()), Some("a"));
    assert_eq!(s.len(), 1);
}

#[test]
fn first_sentence_borrows_original() {
    let text = String::from("Rust is fast. It is also safe.");
    let first;
    {
        let e = Excerpt { text: &text };
        first = e.first_sentence();
    }
    assert_eq!(first, "Rust is fast.");
}

#[test]
fn first_sentence_without_dot() {
    assert_eq!(Excerpt { text: "no dot here" }.first_sentence(), "no dot here");
    assert_eq!(Excerpt { text: "" }.first_sentence(), "");
}
