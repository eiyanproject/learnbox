import math
from abc import ABC, abstractmethod


def _positive(value):
    if value <= 0:
        raise ValueError("must be positive")
    return value


class Shape(ABC):
    @abstractmethod
    def area(self): ...

    @abstractmethod
    def perimeter(self): ...

    def describe(self):
        return f"{type(self).__name__} area={self.area():.2f} perimeter={self.perimeter():.2f}"


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = _positive(value)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = _positive(value)

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

    @Rectangle.width.setter
    def width(self, value):
        Rectangle.width.fset(self, value)
        Rectangle.height.fset(self, value)

    @Rectangle.height.setter
    def height(self, value):
        Rectangle.width.fset(self, value)
        Rectangle.height.fset(self, value)

    @classmethod
    def from_area(cls, area):
        return cls(math.sqrt(area))


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = _positive(value)

    def area(self):
        return math.pi * self.radius**2

    def perimeter(self):
        return 2 * math.pi * self.radius
