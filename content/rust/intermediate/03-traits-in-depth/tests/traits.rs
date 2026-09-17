use traits_in_depth::*;

#[test]
fn money_arithmetic() {
    let a = Money::new(1250);
    let b = Money::new(300);
    assert_eq!(a + b, Money::new(1550));
    assert_eq!(a - b, Money::new(950));
    assert_eq!(b * 3, Money::new(900));
    assert_eq!(-a, Money::new(-1250));
    let mut c = a;
    c += b;
    c += b;
    assert_eq!(c, Money::new(1850));
}

#[test]
fn money_display() {
    assert_eq!(Money::new(1234).to_string(), "12.34");
    assert_eq!(Money::new(5).to_string(), "0.05");
    assert_eq!(Money::new(-50).to_string(), "-0.50");
    assert_eq!(Money::new(100000).to_string(), "1000.00");
}

#[test]
fn stack_container() {
    let s = Stack { items: vec!["a", "b"] };
    assert_eq!(s.get(1), Some(&"b"));
    assert_eq!(s.get(5), None);
    assert_eq!(s.first(), Some(&"a"));
    assert_eq!(s.len(), 2);
    assert!(!s.is_empty());
    let empty: Stack<i32> = Stack { items: vec![] };
    assert!(empty.is_empty() && empty.first().is_none());
}

struct Pair(u8, u8);

impl Container for Pair {
    type Item = u8;
    fn get(&self, i: usize) -> Option<&u8> {
        match i {
            0 => Some(&self.0),
            1 => Some(&self.1),
            _ => None,
        }
    }
    fn len(&self) -> usize {
        2
    }
}

#[test]
fn defaults_work_for_other_implementors() {
    assert_eq!(Pair(7, 9).first(), Some(&7));
    assert_eq!(total_len(&Pair(1, 2), &Stack { items: vec![1.0, 2.0, 3.0] }), 5);
}

#[test]
fn blanket_describe() {
    assert_eq!(42.describe(), "<42>");
    assert_eq!("hi".describe(), "<hi>");
    assert_eq!(Money::new(199).describe(), "<1.99>");
}
