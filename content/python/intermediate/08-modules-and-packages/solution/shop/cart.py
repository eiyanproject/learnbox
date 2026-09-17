from .pricing import TAX_RATE, apply_discount


class Cart:
    def __init__(self):
        self.items = {}  # name -> [price, qty]

    def add(self, name, price, qty=1):
        if name in self.items:
            self.items[name][1] += qty
        else:
            self.items[name] = [price, qty]

    def count(self):
        return sum(qty for _, qty in self.items.values())

    def total(self, discount_percent=0):
        subtotal = sum(price * qty for price, qty in self.items.values())
        return round(apply_discount(subtotal, discount_percent) * (1 + TAX_RATE), 2)
