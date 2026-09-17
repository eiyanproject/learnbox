import importlib
import io
import pathlib
from contextlib import redirect_stdout

import pytest

HERE = pathlib.Path(__file__).parent


def test_package_exports():
    shop = importlib.import_module("shop")
    assert set(shop.__all__) == {"Cart", "apply_discount", "TAX_RATE"}
    assert shop.TAX_RATE == 0.11
    assert shop.Cart is importlib.import_module("shop.cart").Cart


def test_cart_uses_relative_import():
    source = (HERE / "shop" / "cart.py").read_text()
    assert "from .pricing import" in source


def test_apply_discount():
    from shop import apply_discount

    assert apply_discount(200, 25) == 150
    assert apply_discount(99, 0) == 99
    assert apply_discount(50, 100) == 0
    for bad in (-1, 101):
        with pytest.raises(ValueError):
            apply_discount(10, bad)


def test_cart_add_and_count():
    from shop import Cart

    c = Cart()
    c.add("tea", 10000)
    c.add("tea", 10000, 2)
    c.add("cake", 15000)
    assert c.count() == 4


def test_cart_total_with_tax_and_discount():
    from shop import Cart

    c = Cart()
    c.add("coffee", 25000, 2)
    c.add("bread", 18000)
    assert c.total() == 75480.0
    assert c.total(discount_percent=10) == 67932.0


def test_empty_cart():
    from shop import Cart

    assert Cart().total() == 0


def test_main_has_guard():
    buf = io.StringIO()
    with redirect_stdout(buf):
        main = importlib.import_module("main")
    assert buf.getvalue() == "", "importing main.py must not print; use the __main__ guard"
    with redirect_stdout(buf):
        main.main()
    assert "67932.0" in buf.getvalue()
