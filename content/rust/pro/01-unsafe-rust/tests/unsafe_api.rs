use unsafe_rust::*;

#[test]
fn splits_into_two_mutable_halves() {
    let mut data = [1, 2, 3, 4, 5];
    let (left, right) = split_at_mut(&mut data, 2);
    assert_eq!(left, [1, 2]);
    assert_eq!(right, [3, 4, 5]);
    left[0] = 10;
    right[2] = 50;
    assert_eq!(data, [10, 2, 3, 4, 50]);
}

#[test]
fn splits_at_the_edges() {
    let mut data = [1, 2];
    let (l, r) = split_at_mut(&mut data, 0);
    assert!(l.is_empty() && r.len() == 2);
    let (l, r) = split_at_mut(&mut data, 2);
    assert!(l.len() == 2 && r.is_empty());
    let mut empty: [i32; 0] = [];
    let (l, r) = split_at_mut(&mut empty, 0);
    assert!(l.is_empty() && r.is_empty());
}

#[test]
#[should_panic]
fn split_past_the_end_panics() {
    let mut data = [1, 2, 3];
    split_at_mut(&mut data, 4);
}

#[test]
fn swaps_by_pointer() {
    let mut data = [1, 2, 3];
    unsafe {
        swap_unchecked(&mut data, 0, 2);
        swap_unchecked(&mut data, 1, 1);
    }
    assert_eq!(data, [3, 2, 1]);
}

#[test]
fn buffer_grows_by_doubling() {
    let mut b = Buffer::new();
    assert_eq!((b.len(), b.capacity()), (0, 0));
    for byte in b"hello" {
        b.push(*byte);
    }
    assert_eq!(b.len(), 5);
    assert_eq!(b.capacity(), 8);
    for _ in 0..4 {
        b.push(b'!');
    }
    assert_eq!(b.len(), 9);
    assert_eq!(b.capacity(), 16);
}

#[test]
fn buffer_as_str() {
    let mut b = Buffer::new();
    b.extend("héllo".bytes());
    assert_eq!(b.as_bytes().len(), 6);
    assert_eq!(b.as_str(), Some("héllo"));
    assert_eq!(unsafe { b.as_str_unchecked() }, "héllo");

    let mut bad = Buffer::new();
    bad.push(0xff);
    assert_eq!(bad.as_str(), None);
}

#[test]
fn unsafe_blocks_are_justified() {
    let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    let blocks = src.matches("unsafe {").count();
    let comments = src.to_uppercase().matches("SOUND").count() + src.to_uppercase().matches("SAFETY:").count();
    assert!(blocks > 0, "no unsafe blocks at all?");
    assert!(comments >= blocks, "every unsafe block needs a comment saying why it is sound");
}
