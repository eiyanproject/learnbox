from typing import Generic, Iterable, Protocol, Sequence, TypedDict, TypeVar, runtime_checkable

T = TypeVar("T")


def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

    def __len__(self) -> int:
        return len(self._items)


@runtime_checkable
class SupportsArea(Protocol):
    def area(self) -> float: ...


def total_area(shapes: Iterable[SupportsArea]) -> float:
    return sum(s.area() for s in shapes)


class Config(TypedDict):
    host: str
    port: int
    debug: bool


def parse_config(raw: dict[str, str]) -> Config:
    return Config(
        host=raw["host"],
        port=int(raw["port"]),
        debug=raw.get("debug", "").lower() in ("1", "true", "yes"),
    )
