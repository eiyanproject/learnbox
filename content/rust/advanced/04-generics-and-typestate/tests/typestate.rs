use generics_typestate::*;

#[test]
fn associated_constants() {
    assert_eq!(Triangle::SIDES, 3);
    assert_eq!(<Square as Shape>::name(), "square");
    assert_eq!(total_sides::<Triangle, Square>(), 7);
    assert_eq!(total_sides::<Square, Square>(), 8);
}

#[test]
fn tagged_meters() {
    let h: Meters<Height> = Meters::new(2.0);
    let w: Meters<Width> = Meters::new(3.5);
    assert_eq!(h.value(), 2.0);
    assert_eq!(area(h, w), 7.0);
    assert_eq!(std::mem::size_of::<Meters<Height>>(), std::mem::size_of::<f64>());
}

#[test]
fn request_builder() {
    let r = Request::new().url("https://example.com").header("Accept", "json").header("X-Id", "7");
    assert_eq!(r.send(), "GET https://example.com [Accept: json, X-Id: 7]");
    assert_eq!(Request::new().url("/health").send(), "GET /health []");
}

#[test]
fn typestate_types() {
    fn is_ready(_: &Request<HasUrl>) {}
    let r = Request::new().url("/x");
    is_ready(&r);
    let _empty: Request<Empty> = Request::new();
}

#[test]
fn largest_by_key() {
    let words = ["pear", "fig", "banana", "kiwi"];
    assert_eq!(largest_by(&words, |w| w.len()), Some(&"banana"));
    assert_eq!(largest_by(&[3.5, -1.0, 9.25], |x| *x), Some(&9.25));
    assert_eq!(largest_by(&words, |w| w.chars().last()), Some(&"pear"));
    let empty: [i32; 0] = [];
    assert_eq!(largest_by(&empty, |x| *x), None);
}

#[test]
fn invalid_transitions_do_not_compile() {
    // Request::new().send() and Request::new().header(..) must not exist.
    // Checked from the source, since a test cannot contain code that fails to compile.
    let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    let empty_impl = src.split("impl Request<Empty>").nth(1).expect("impl Request<Empty> block");
    let empty_block = &empty_impl[..empty_impl.find("\nimpl").unwrap_or(empty_impl.len())];
    assert!(!empty_block.contains("fn send"), "send belongs only to Request<HasUrl>");
    assert!(!empty_block.contains("fn header"), "header belongs only to Request<HasUrl>");
}
