import math

import pytest

from shapes import Circle, Rectangle, Shape, Square


def test_shape_is_abstract():
    with pytest.raises(TypeError):
        Shape()


def test_incomplete_subclass_cannot_be_created():
    class Blob(Shape):
        def area(self):
            return 1

    with pytest.raises(TypeError):
        Blob()


def test_rectangle():
    r = Rectangle(3, 4)
    assert isinstance(r, Shape)
    assert r.area() == 12
    assert r.perimeter() == 14
    assert r.describe() == "Rectangle area=12.00 perimeter=14.00"


def test_rectangle_validation():
    with pytest.raises(ValueError):
        Rectangle(0, 5)
    r = Rectangle(1, 1)
    with pytest.raises(ValueError):
        r.height = -2
    assert r.height == 1


def test_width_is_a_property():
    assert isinstance(Rectangle.__dict__.get("width"), property)


def test_square_keeps_sides_equal():
    s = Square(2)
    assert isinstance(s, Rectangle)
    s.width = 5
    assert (s.width, s.height) == (5, 5)
    s.height = 3
    assert (s.width, s.height) == (3, 3)
    assert s.describe() == "Square area=9.00 perimeter=12.00"


def test_square_from_area():
    s = Square.from_area(49)
    assert type(s) is Square
    assert s.width == 7


def test_square_from_area_respects_subclass():
    class Tile(Square):
        pass

    assert type(Tile.from_area(4)) is Tile


def test_circle():
    c = Circle(2)
    assert math.isclose(c.area(), 4 * math.pi)
    assert c.describe() == "Circle area=12.57 perimeter=12.57"
    with pytest.raises(ValueError):
        c.radius = 0
