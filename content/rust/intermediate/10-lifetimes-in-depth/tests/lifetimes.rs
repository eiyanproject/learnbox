use lifetimes_in_depth::*;

#[test]
fn tokens_outlive_the_tokenizer() {
    let text = String::from("  let x =\t42 ;\n");
    let tokens: Vec<&str> = {
        let t = Tokenizer::new(&text);
        t.collect()
    };
    assert_eq!(tokens, ["let", "x", "=", "42", ";"]);
}

#[test]
fn tokens_are_slices_of_input() {
    let text = String::from("héllo wörld");
    let mut t = Tokenizer::new(&text);
    let first = t.next().unwrap();
    let second = t.next().unwrap();
    assert_eq!((first, second), ("héllo", "wörld"));
    assert_eq!(first.as_ptr(), text.as_ptr());
    assert_eq!(t.next(), None);
    assert_eq!(Tokenizer::new("   ").next(), None);
}

#[test]
fn longest() {
    assert_eq!(longest_line("a\nbbb\ncc\nddd"), "bbb");
    assert_eq!(longest_line(""), "");
}

#[test]
fn pick_first_is_tied_only_to_first() {
    let kept = String::from("kept");
    let result;
    {
        let temporary = String::from("temporary value");
        result = pick_first(&kept, &temporary);
    }
    assert_eq!(result, "kept");
}

#[test]
fn registry_of_static_names() {
    let mut r = Registry::new();
    r.register("zeta");
    r.register("alpha");
    let name: &'static str = r.names()[0];
    assert_eq!(name, "alpha");
    assert_eq!(r.names(), ["alpha", "zeta"]);
}
