use custom_iterators::*;

#[test]
fn fibonacci_start() {
    let v: Vec<u64> = Fibonacci::new().take(10).collect();
    assert_eq!(v, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]);
}

#[test]
fn fibonacci_ends_before_overflow() {
    let all: Vec<u64> = Fibonacci::new().collect();
    assert_eq!(all.len(), 94);
    assert_eq!(*all.last().unwrap(), 12200160415121876738);
}

#[test]
fn fibonacci_works_with_adapters() {
    let even_sum: u64 = Fibonacci::new().take_while(|&x| x < 4_000_000).filter(|x| x % 2 == 0).sum();
    assert_eq!(even_sum, 4613732);
}

#[test]
fn countdown_forward_and_back() {
    assert_eq!(Countdown::new(3).collect::<Vec<_>>(), [3, 2, 1]);
    assert_eq!(Countdown::new(3).rev().collect::<Vec<_>>(), [1, 2, 3]);
    assert_eq!(Countdown::new(0).count(), 0);
}

#[test]
fn countdown_meets_in_the_middle() {
    let mut c = Countdown::new(4);
    assert_eq!(c.next(), Some(4));
    assert_eq!(c.next_back(), Some(1));
    assert_eq!(c.size_hint(), (2, Some(2)));
    assert_eq!(c.next(), Some(3));
    assert_eq!(c.next_back(), Some(2));
    assert_eq!(c.next(), None);
    assert_eq!(c.next_back(), None);
}

#[test]
fn ring_for_loops() {
    let ring = Ring { items: vec![String::from("a"), String::from("b")] };
    let mut seen = Vec::new();
    for s in &ring {
        seen.push(s.len());
    }
    assert_eq!(seen, [1, 1]);
    let owned: Vec<String> = ring.into_iter().collect();
    assert_eq!(owned, ["a", "b"]);
}

#[test]
fn every_nth_on_any_iterator() {
    assert_eq!((0..10).every_nth(3).collect::<Vec<_>>(), [0, 3, 6, 9]);
    assert_eq!("abcdef".chars().every_nth(2).collect::<String>(), "ace");
    assert_eq!(Fibonacci::new().every_nth(1).take(3).collect::<Vec<_>>(), [0, 1, 1]);
}
