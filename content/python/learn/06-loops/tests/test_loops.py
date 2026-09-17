from loops import collatz_steps, first_repeated, fizzbuzz, sum_to


def test_sum_to():
    assert sum_to(10) == 55
    assert sum_to(1) == 1
    assert sum_to(0) == 0
    assert sum_to(1000) == 500500


def test_fizzbuzz_first_five():
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fizzbuzz_fifteen():
    result = fizzbuzz(15)
    assert len(result) == 15
    assert result[14] == "FizzBuzz"
    assert result[8] == "Fizz"
    assert result[9] == "Buzz"


def test_fizzbuzz_empty():
    assert fizzbuzz(0) == []


def test_collatz():
    assert collatz_steps(1) == 0
    assert collatz_steps(6) == 8
    assert collatz_steps(27) == 111


def test_first_repeated():
    assert first_repeated(["a", "b", "c", "b", "a"]) == "b"
    assert first_repeated(["x", "y", "x"]) == "x"


def test_first_repeated_none():
    assert first_repeated(["one", "two", "three"]) is None
    assert first_repeated([]) is None
