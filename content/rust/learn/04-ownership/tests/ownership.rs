use ownership::*;

fn strings(v: &[&str]) -> Vec<String> {
    v.iter().map(|s| s.to_string()).collect()
}

#[test]
fn exclaim_appends() {
    assert_eq!(exclaim(String::from("hello")), "hello!");
    assert_eq!(exclaim(String::new()), "!");
}

#[test]
fn first_and_count_works() {
    assert_eq!(first_and_count(strings(&["ana", "budi", "citra"])), ("ana".to_string(), 3));
}

#[test]
fn twice_gives_two_copies() {
    let (a, b) = twice(String::from("echo"));
    assert_eq!(a, "echo");
    assert_eq!(b, "echo");
}

#[test]
fn shout_all_uppercases() {
    assert_eq!(shout_all(strings(&["hi", "there"])), strings(&["HI", "THERE"]));
    assert_eq!(shout_all(Vec::new()), Vec::<String>::new());
}
