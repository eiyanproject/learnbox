class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        self.history.append(("withdraw", amount))

    def transfer_to(self, other, amount):
        self.withdraw(amount)
        other.deposit(amount)

    def __repr__(self):
        return f"Account({self.owner!r}, {self.balance})"

    def __eq__(self, other):
        return isinstance(other, Account) and (self.owner, self.balance) == (other.owner, other.balance)
