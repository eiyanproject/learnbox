class Field:
    def __set_name__(self, owner, name):
        self.name = name
        self.storage = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.storage, value)

    def validate(self, value):
        pass


class String(Field):
    def __init__(self, max_length):
        self.max_length = max_length

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a str")
        if len(value) > self.max_length:
            raise ValueError(f"{self.name} is longer than {self.max_length}")


class Positive(Field):
    def validate(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")


class NonNegativeInt(Field):
    def validate(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{self.name} must be an int")
        if value < 0:
            raise ValueError(f"{self.name} cannot be negative")


class Product:
    __slots__ = ("_name", "_price", "_quantity")

    name = String(40)
    price = Positive()
    quantity = NonNegativeInt()

    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def total(self):
        return self.price * self.quantity
