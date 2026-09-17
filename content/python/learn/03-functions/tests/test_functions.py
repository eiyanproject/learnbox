from functions import bmi, greet, split_bill, square


def test_square():
    assert square(4) == 16
    assert square(-3) == 9
    assert square(0) == 0


def test_square_returns_rather_than_prints():
    assert square(5) is not None, "square() did not return anything"


def test_greet_default():
    assert greet("Ana") == "Hello, Ana!"


def test_greet_custom_greeting():
    assert greet("Budi", "Hi") == "Hi, Budi!"
    assert greet(greeting="Welcome", name="Citra") == "Welcome, Citra!"


def test_bmi_rounded():
    assert bmi(70, 1.75) == 22.9
    assert bmi(50, 1.6) == 19.5


def test_split_bill_even():
    assert split_bill(90, 3) == (30.0, 0.0)


def test_split_bill_leftover():
    share, leftover = split_bill(100, 3)
    assert share == 33.33
    assert leftover == 0.01
