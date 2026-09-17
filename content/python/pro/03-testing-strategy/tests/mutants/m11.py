# total_units counts items instead of units
class Inventory:
    """Stock levels for named items."""

    def __init__(self):
        self._stock = {}

    def add(self, item, qty):
        """Add qty (must be > 0, else ValueError) units of item."""
        if qty <= 0:
            raise ValueError("quantity must be positive")
        self._stock[item] = self._stock.get(item, 0) + qty

    def remove(self, item, qty):
        """Remove qty (> 0) units. Removing more than is in stock raises
        ValueError("not enough ...") and leaves stock unchanged. An item whose
        stock reaches exactly 0 is forgotten: it no longer appears in items()."""
        if qty <= 0:
            raise ValueError("quantity must be positive")
        have = self._stock.get(item, 0)
        if qty > have:
            raise ValueError(f"not enough {item}: have {have}, need {qty}")
        if have == qty:
            del self._stock[item]
        else:
            self._stock[item] = have - qty

    def stock(self, item):
        """Units of item in stock; 0 for unknown items."""
        return self._stock.get(item, 0)

    def items(self):
        """Names of items with stock, sorted alphabetically."""
        return sorted(self._stock)

    def low_stock(self, threshold):
        """Items with stock less than or equal to threshold, sorted by stock
        (lowest first), then by name."""
        low = [(qty, name) for name, qty in self._stock.items() if qty <= threshold]
        return [name for qty, name in sorted(low)]

    def total_units(self):
        """Sum of all stock."""
        return len(self._stock)
