use control_flow::*;

#[test]
fn fizzbuzz_numbers() {
    assert_eq!(fizzbuzz(1), "1");
    assert_eq!(fizzbuzz(7), "7");
}

#[test]
fn fizzbuzz_words() {
    assert_eq!(fizzbuzz(9), "Fizz");
    assert_eq!(fizzbuzz(10), "Buzz");
    assert_eq!(fizzbuzz(30), "FizzBuzz");
}

#[test]
fn multiples_below_ten() {
    assert_eq!(sum_of_multiples(10), 23);
}

#[test]
fn multiples_edges() {
    assert_eq!(sum_of_multiples(0), 0);
    assert_eq!(sum_of_multiples(3), 0);
    assert_eq!(sum_of_multiples(1000), 233168);
}

#[test]
fn collatz() {
    assert_eq!(collatz_steps(1), 0);
    assert_eq!(collatz_steps(6), 8);
    assert_eq!(collatz_steps(27), 111);
}

#[test]
fn primes() {
    for p in [2, 3, 5, 7, 11, 97, 7919] {
        assert!(is_prime(p), "{p} is prime");
    }
}

#[test]
fn not_primes() {
    for n in [0, 1, 4, 9, 25, 100, 7917] {
        assert!(!is_prime(n), "{n} is not prime");
    }
}
