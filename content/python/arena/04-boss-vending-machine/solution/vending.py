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


def coins_for(amount):
    out = []
    for coin in COINS:
        while amount >= coin:
            out.append(coin)
            amount -= coin
    return out


class VendingMachine:
    def __init__(self, stock):
        self._prices = {name: price for name, (price, _) in stock.items()}
        self._left = {name: quantity for name, (_, quantity) in stock.items()}
        self.credit = 0
        self.sales = 0

    def insert(self, coin):
        if coin not in COINS:
            raise InvalidCoin(coin)
        self.credit += coin
        return self.credit

    def refund(self):
        coins = coins_for(self.credit)
        self.credit = 0
        return coins

    def buy(self, name):
        if name not in self._prices:
            raise UnknownItem(name)
        if self._left[name] == 0:
            raise SoldOut(name)
        price = self._prices[name]
        if self.credit < price:
            raise NotEnoughCredit(name)
        self._left[name] -= 1
        self.sales += price
        change = coins_for(self.credit - price)
        self.credit = 0
        return change

    def available(self):
        return sorted(name for name, left in self._left.items() if left > 0)

    def quantity(self, name):
        if name not in self._left:
            raise UnknownItem(name)
        return self._left[name]
