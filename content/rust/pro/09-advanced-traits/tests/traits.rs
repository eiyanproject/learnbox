use advanced_traits::*;

#[test]
fn lending_iterator_yields_mutable_windows() {
    let mut data = [1, 2, 3, 4];
    let mut windows = WindowsMut::new(&mut data, 2);
    while let Some(window) = windows.next() {
        window[0] += 10;
    }
    assert_eq!(data, [11, 12, 13, 4]);
}

#[test]
fn window_edges() {
    let mut data = [1, 2, 3];
    assert!(WindowsMut::new(&mut data, 4).next().is_none());
    assert!(WindowsMut::new(&mut data, 0).next().is_none());
    let mut three = WindowsMut::new(&mut data, 3);
    assert_eq!(three.next().map(|w| w.to_vec()), Some(vec![1, 2, 3]));
    assert!(three.next().is_none());
}

#[test]
fn window_count() {
    let mut data = [0; 10];
    let mut w = WindowsMut::new(&mut data, 3);
    let mut seen = 0;
    while w.next().is_some() {
        seen += 1;
    }
    assert_eq!(seen, 8);
}

#[test]
fn pipeline_returns_impl_iterator() {
    let p = Simple { steps: vec!["read".into(), "transform".into(), "write".into()] };
    assert_eq!(p.steps().collect::<Vec<_>>(), ["read", "transform", "write"]);
    assert_eq!(p.describe(), "read -> transform -> write");
}

#[test]
fn repository_works_as_a_trait_object() {
    let repos: Vec<Box<dyn Repository>> = vec![
        Box::new(MemoryRepo { name: "users".into(), items: vec!["ana".into(), "budi".into()] }),
        Box::new(MemoryRepo { name: "posts".into(), items: vec!["hello".into()] }),
    ];
    assert_eq!(repos[0].name(), "users");
    assert_eq!(repos[0].find(1), Some("budi".to_string()));
    assert_eq!(repos[1].find(9), None);
    assert_eq!(repos[0].all().collect::<Vec<_>>(), ["ana", "budi"]);
    assert_eq!(count_all(&repos), 3);
}

#[test]
fn associated_type_bounds() {
    assert_eq!(total_len(["ab", "cde"]), 5);
    assert_eq!(total_len(vec![String::from("hello")]), 5);
    assert_eq!(total_len(Vec::<String>::new()), 0);
    let owned: Vec<Box<str>> = vec!["xy".into()];
    assert_eq!(total_len(owned), 2);
}
