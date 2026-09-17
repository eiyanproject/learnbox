use iterators_and_closures::*;

#[test]
fn squares_of_evens() {
    assert_eq!(evens_squared(&[1, 2, 3, 4, -6]), vec![4, 16, 36]);
    assert_eq!(evens_squared(&[1, 3]), Vec::<i32>::new());
}

#[test]
fn long_words() {
    assert_eq!(count_long_words("a quick brown fox jumps", 5), 3);
    assert_eq!(count_long_words("", 1), 0);
    assert_eq!(count_long_words("a bb ccc", 0), 3);
}

#[test]
fn totals() {
    assert_eq!(running_totals(&[1, 2, 3, 4]), vec![1, 3, 6, 10]);
    assert_eq!(running_totals(&[5, -5, 5]), vec![5, 0, 5]);
    assert_eq!(running_totals(&[]), Vec::<i32>::new());
}

#[test]
fn adders() {
    let add5 = make_adder(5);
    let sub2 = make_adder(-2);
    assert_eq!(add5(10), 15);
    assert_eq!(sub2(10), 8);
    assert_eq!(add5(sub2(0)), 3);
}

#[test]
fn apply_repeatedly() {
    assert_eq!(apply_n(|x| x * 2, 10, 1), 1024);
    assert_eq!(apply_n(|x| x + 1, 0, 7), 7);
    assert_eq!(apply_n(make_adder(3), 4, 0), 12);
}
