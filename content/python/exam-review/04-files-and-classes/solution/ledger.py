class Ledger:
    def __init__(self):
        self.entries = []

    def add(self, name, amount):
        self.entries.append((name, amount))

    def total(self):
        return sum(amount for _, amount in self.entries)

    def top_spender(self):
        if not self.entries:
            return None
        totals = {}
        for name, amount in self.entries:
            totals[name] = totals.get(name, 0) + amount
        ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[0][0]

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for name, amount in self.entries:
                f.write(f"{name},{amount}\n")

    @classmethod
    def load(cls, path):
        ledger = cls()
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                name, amount = line.rsplit(",", 1)
                ledger.add(name, float(amount))
        return ledger
