class VendingError(Exception):
    """Anything the machine refuses to do."""


class InvalidCoin(VendingError):
    pass


class UnknownItem(VendingError):
    pass


class SoldOut(VendingError):
    pass


class NotEnoughCredit(VendingError):
    pass


COINS = [500, 100, 50, 10]


class VendingMachine:
    def __init__(self, stock):
        pass
