import pytest

from decorators import count_calls, memoize, retry, uppercase_result


def test_count_calls():
    @count_calls
    def add(a, b):
        return a + b

    assert add.calls == 0
    assert add(2, 3) == 5
    add(1, b=1)
    assert add.calls == 2


def test_wraps_keeps_identity():
    @count_calls
    def documented():
        """Docs survive."""

    @uppercase_result
    def name():
        return "x"

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "Docs survive."
    assert name.__name__ == "name"


def test_retry_eventually_succeeds():
    attempts = []

    @retry(3)
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("try again")
        return "ok"

    assert flaky() == "ok"
    assert len(attempts) == 3


def test_retry_gives_up():
    attempts = []

    @retry(2)
    def broken():
        attempts.append(1)
        raise ValueError(f"attempt {len(attempts)}")

    with pytest.raises(ValueError, match="attempt 2"):
        broken()
    assert len(attempts) == 2


def test_retry_keeps_name():
    @retry(1)
    def f():
        return 1

    assert f.__name__ == "f"


def test_memoize_runs_once_per_argument():
    runs = []

    @memoize
    def slow_square(n):
        runs.append(n)
        return n * n

    assert slow_square(4) == 16
    assert slow_square(4) == 16
    assert slow_square(5) == 25
    assert runs == [4, 5]


def test_memoize_fibonacci_is_fast():
    @memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(200) == 280571172992510140037611932413038677189525


def test_uppercase_result():
    @uppercase_result
    def greet(name, punctuation="!"):
        return f"hello {name}{punctuation}"

    assert greet("ana") == "HELLO ANA!"
    assert greet("budi", punctuation="?") == "HELLO BUDI?"
