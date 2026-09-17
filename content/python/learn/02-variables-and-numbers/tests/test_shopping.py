import pytest

import shopping


def test_apples_total():
    assert shopping.apples_total == pytest.approx(5.40)


def test_bread_total():
    assert shopping.bread_total == pytest.approx(4.70)


def test_total_is_rounded():
    assert shopping.total == 10.10


def test_change():
    assert shopping.change == 9.90


def test_full_boxes_of_six():
    assert shopping.boxes == 6
    assert isinstance(shopping.boxes, int), "use // so the result is a whole number"


def test_loose_eggs():
    assert shopping.loose_eggs == 4


def test_prices_were_not_changed():
    assert (shopping.apple_price, shopping.apple_count) == (0.45, 12)
    assert (shopping.bread_price, shopping.bread_count, shopping.eggs) == (2.35, 2, 40)
