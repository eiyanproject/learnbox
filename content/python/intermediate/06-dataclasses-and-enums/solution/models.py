from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(order=True)
class Task:
    sort_key: tuple = field(init=False, repr=False)
    title: str = field(compare=False)
    priority: Priority = field(default=Priority.MEDIUM, compare=False)
    tags: list[str] = field(default_factory=list, compare=False)
    done: bool = field(default=False, compare=False)

    def __post_init__(self):
        self.sort_key = (-self.priority.value, self.title)


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("amount cannot be negative")

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError(f"cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
