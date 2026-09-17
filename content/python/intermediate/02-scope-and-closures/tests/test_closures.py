from closures import make_accumulator, make_adders, make_counter, make_multiplier


def test_counter_counts():
    c = make_counter()
    assert [c(), c(), c()] == [1, 2, 3]


def test_counter_start_and_independence():
    a = make_counter(10)
    b = make_counter()
    assert a() == 11
    assert b() == 1
    assert a() == 12


def test_multiplier():
    double = make_multiplier(2)
    triple = make_multiplier(3)
    assert double(21) == 42
    assert triple(5) == 15


def test_accumulator_running_average():
    add = make_accumulator()
    assert add(10) == 10
    assert add(20) == 15
    assert add(30) == 20


def test_accumulators_are_independent():
    a, b = make_accumulator(), make_accumulator()
    a(100)
    assert b(2) == 2


def test_adders_capture_each_value():
    adders = make_adders(4)
    assert [f(10) for f in adders] == [10, 11, 12, 13]
