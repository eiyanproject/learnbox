import pytest

from fields import Field, NonNegativeInt, Positive, Product, String


def test_product_happy_path():
    p = Product("kopi", 25000, 3)
    assert (p.name, p.price, p.quantity) == ("kopi", 25000, 3)
    assert p.total() == 75000


def test_descriptors_are_class_attributes():
    for attr, kind in [("name", String), ("price", Positive), ("quantity", NonNegativeInt)]:
        d = Product.__dict__[attr]
        assert isinstance(d, kind) and isinstance(d, Field)
        assert getattr(Product, attr) is d, "accessing on the class should return the descriptor"
        assert d.name == attr


def test_string_validation():
    with pytest.raises(TypeError):
        Product(123, 1, 1)
    with pytest.raises(ValueError, match="name"):
        Product("x" * 41, 1, 1)
    Product("x" * 40, 1, 1)


def test_positive_validation():
    p = Product("a", 1.5, 1)
    with pytest.raises(ValueError, match="price"):
        p.price = 0
    with pytest.raises(TypeError):
        p.price = "10"
    with pytest.raises(TypeError):
        p.price = True
    assert p.price == 1.5


def test_non_negative_int_validation():
    p = Product("a", 1, 0)
    with pytest.raises(ValueError, match="quantity"):
        p.quantity = -1
    with pytest.raises(TypeError):
        p.quantity = 2.5
    with pytest.raises(TypeError):
        p.quantity = False


def test_same_descriptor_class_reused_independently():
    class Box:
        width = Positive()
        height = Positive()

    b = Box()
    b.width, b.height = 2, 3
    assert (b.width, b.height) == (2, 3)


def test_slots_block_new_attributes():
    p = Product("a", 1, 1)
    assert not hasattr(p, "__dict__")
    with pytest.raises(AttributeError):
        p.colour = "red"
