---
title: Testing strategy
summary: Write tests that actually catch bugs. Your tests are graded by running them against broken versions of the code.
order: 3
files: [test_inventory.py, inventory.py]
run: python -m pytest -q test_inventory.py
hints:
  - "Test every rule in the docstrings, including the edges: removing exactly the stock on hand, removing one more than that, and quantities of zero or less."
  - "Check error cases with `with pytest.raises(ValueError):`, and check that a failed operation left the stock unchanged."
  - "`low_stock(threshold)` has a boundary: is an item with exactly `threshold` units low? Read the docstring and test both sides of it."
  - "Use `@pytest.fixture` for an `Inventory` pre-filled with a few items, and `@pytest.mark.parametrize` for tables of inputs and expected results."
---

This lesson turns things around. The code is written and correct. **You write
the tests**, and **Check** grades them by running your tests against several
subtly broken versions of `inventory.py` (**mutants**). A good test suite fails
on every mutant and passes on the real code.

This is **mutation testing**, and it answers the question code coverage cannot:
"if this line were wrong, would any test notice?"

## pytest essentials

```python
import pytest
from inventory import Inventory

def test_add_increases_stock():
    inv = Inventory()
    inv.add("apple", 3)
    assert inv.stock("apple") == 3
```

Plain `assert` statements; pytest rewrites them to show both sides on failure.

## Expecting errors

```python
def test_cannot_remove_more_than_stock():
    inv = Inventory()
    inv.add("apple", 2)
    with pytest.raises(ValueError, match="not enough"):
        inv.remove("apple", 3)
    assert inv.stock("apple") == 2        # and nothing changed
```

## Fixtures

Shared setup, injected by parameter name, fresh for each test:

```python
@pytest.fixture
def stocked():
    inv = Inventory()
    inv.add("apple", 5)
    inv.add("pear", 1)
    return inv

def test_low_stock(stocked):
    assert stocked.low_stock(2) == ["pear"]
```

Built-in fixtures include `tmp_path` (a fresh directory), `capsys` (captured
output) and `monkeypatch` (temporarily replace attributes and environment variables).

## Parametrize

One test body, many cases, each reported separately:

```python
@pytest.mark.parametrize("qty", [0, -1, -100])
def test_add_rejects_non_positive(qty):
    with pytest.raises(ValueError):
        Inventory().add("apple", qty)
```

## What makes tests catch bugs

- **Boundaries.** Off-by-one mutants (`<` instead of `<=`) survive unless a test
  uses exactly the boundary value.
- **Both outcomes.** Test that valid input works *and* invalid input is rejected.
- **State after failure.** An operation that raises halfway through can leave
  data corrupted; assert that it did not.
- **Exact values**, not just "truthy" or "not None".
- **One behaviour per test**, named after the behaviour, so a failure tells you
  what broke.

## Your turn

Read the docstrings in `inventory.py` carefully: they are the specification.
Write tests in `test_inventory.py` so that:

1. they all pass against the real `inventory.py`, and
2. every hidden mutant makes at least one of them fail.

Do not change `inventory.py` (the grader uses its own copy). Use **Run** to run
your tests; **Check** reports which mutants survived.
