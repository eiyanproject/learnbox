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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **test** | code that runs other code and checks the result |
| **test suite** | all of a project's tests together |
| **mutant** | a copy of the code with one small, deliberate bug, such as `<` for `<=` |
| **mutation testing** | grading tests by whether they fail on every mutant |
| **kill a mutant** | make it fail at least one test; a mutant that passes **survives** |
| **code coverage** | which lines the tests ran; it says nothing about whether they checked anything |
| **assertion** | a check that must be true, written with `assert` |
| **arrange, act, assert** | set up the situation, do the one thing tested, check the result |
| **fixture** | a function marked `@pytest.fixture` that builds a starting point; a test gets it by naming a parameter after it |
| **parametrize** | running one test body once for each input in a list |
| **boundary value** | the exact edge of a rule, such as exactly the threshold; where off-by-one bugs hide |
| **off-by-one** | a bug that is wrong by one at an edge: `<` instead of `<=` |
| **specification** | the rules the code must follow; here, the docstrings |
| **stock** / **threshold** | how many units are on hand / the limit at or below which an item counts as low |

### Python and pytest names

| Name | What it does |
|---|---|
| `import pytest` | the testing framework |
| `def test_...():` | a test function, found by its name in a `test_*.py` file |
| `assert inv.stock("apple") == 3` | fails the test if false; pytest shows both sides |
| `with pytest.raises(ValueError, match="not enough"):` | fails unless the block raises that exception with a message matching the pattern |
| `@pytest.fixture` | marks a fixture |
| `@pytest.mark.parametrize("qty", [0, -1])` | runs the test once per value |
| `@pytest.mark.parametrize("a, b, c", [(5, 2, 3), ...])` | several parameters as a table |
| `tmp_path`, `capsys`, `monkeypatch` | built-in fixtures: a fresh folder; captured output; temporary replacements |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -m pytest -q test_inventory.py` | runs the tests quietly: a dot per pass, `F` per failure |

### Errors

| Error | Means |
|---|---|
| `AssertionError` | an `assert` was false: the test failed |
| `ValueError` | what `Inventory` raises for bad quantities or not enough stock |

---

Every lesson so far has had hidden tests that checked your code. This
lesson turns things around. The code is written and correct. **You write
the tests**, and **Check** grades them by running your tests against several
subtly broken versions of `inventory.py`, called **mutants**. Each mutant has
one small, deliberate bug, such as `<` where the real code has `<=`. A good
test suite fails on every mutant and passes on the real code.

This is **mutation testing**, and it answers a question that code coverage
cannot. Coverage tells you which lines your tests *ran*. It does not tell
you whether the tests *checked* anything about them. A test that calls every
function and asserts nothing has 100% coverage and catches no bugs at all.
Mutation testing asks the real question: "if this line were wrong, would any
test notice?"

## pytest essentials

pytest finds tests by name: in files named `test_*.py`, it runs every
function whose name starts with `test_`. Inside, you write plain `assert`
statements:

```python
import pytest
from inventory import Inventory

def test_add_increases_stock():
    inv = Inventory()
    inv.add("apple", 3)
    assert inv.stock("apple") == 3
```

A test passes if it finishes, and fails if an `assert` is false or an
exception escapes. pytest rewrites the `assert` statements as it loads the
file, so that a failure shows both sides of the comparison, not only
"AssertionError":

```text
    def test_add_increases_stock():
        inv = Inventory()
        inv.add("apple", 3)
>       assert inv.stock("apple") == 4
E       AssertionError: assert 3 == 4
E        +  where 3 = stock('apple')
```

Run the tests in the terminal with `python -m pytest -q test_inventory.py`
(this lesson's **Run** button). `-q` makes the output quieter: one dot per
passing test, an `F` per failure, and the details of each failure.

Most tests follow the same three-part shape, sometimes called
**arrange, act, assert**: set up the situation (`inv = Inventory()`), do the
one thing being tested (`inv.add("apple", 3)`), and check the result.

## Expecting errors

Code that should reject bad input needs a test that the rejection actually
happens. `pytest.raises` is a context manager that fails the test unless the
block inside it raises the given exception:

```python
def test_cannot_remove_more_than_stock():
    inv = Inventory()
    inv.add("apple", 2)
    with pytest.raises(ValueError, match="not enough"):
        inv.remove("apple", 3)
    assert inv.stock("apple") == 2        # and nothing changed
```

`match=` is a regular expression that must be found in the exception's
message, which checks that the error raised is the one you meant and not
some other `ValueError`. The last line matters as much as the `raises`: a
mutant that subtracts the stock *before* checking would still raise, but
would leave the stock wrong. Only a test that looks at the state afterwards
catches it.

## Fixtures

Many tests need the same starting point, such as an inventory with a few
items in it. A **fixture** is a function marked `@pytest.fixture` that builds
that starting point. A test asks for it by having a parameter with the
fixture's name, and pytest calls the fixture and passes in the result:

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

The fixture runs again for each test that uses it, so every test gets a
fresh inventory, and one test changing it cannot affect another.

pytest also has built-in fixtures, which you request the same way, by
parameter name: `tmp_path` (a fresh empty directory, as a `Path`), `capsys`
(captures what the code prints, so you can check it) and `monkeypatch`
(temporarily replaces attributes and environment variables, and puts them
back after the test).

## Parametrize

When the same check applies to many inputs, writing one test per input is
repetitive. `@pytest.mark.parametrize` runs one test body once for each value
in a list, and reports each case separately, so you can see exactly which
input failed:

```python
@pytest.mark.parametrize("qty", [0, -1, -100])
def test_add_rejects_non_positive(qty):
    with pytest.raises(ValueError):
        Inventory().add("apple", qty)
```

The first argument names the parameter, and the list gives its values; this
produces three tests. Several parameters at once are written as one string
and a list of tuples, which makes a neat table of inputs and expected
results:

```python
@pytest.mark.parametrize("added, removed, left", [(5, 2, 3), (5, 5, 0), (1, 1, 0)])
def test_remove_leaves_the_difference(added, removed, left):
    inv = Inventory()
    inv.add("apple", added)
    inv.remove("apple", removed)
    assert inv.stock("apple") == left
```

## What makes tests catch bugs

The starter `test_inventory.py` has one test, and it shows the main
weakness to avoid: it checks `inv.stock("apple") > 0` after adding 3. A
mutant that added 1 instead of 3, or added the quantity twice, would still
pass it. These are the habits that catch mutants:

- **Boundaries.** Off-by-one mutants (`<` instead of `<=`) survive unless a
  test uses exactly the boundary value. If the rule is "less than or equal to
  the threshold", test an item with *exactly* the threshold, and one with one
  more.
- **Both outcomes.** Test that valid input works *and* that invalid input is
  rejected. A mutant that removes a check entirely only fails a test that
  tries the invalid case.
- **State after failure.** An operation that raises halfway through can leave
  data corrupted; assert that it did not, as in the `remove` example above.
- **Exact values**, not merely "truthy" or "not None": `== 3`, not `> 0`. A
  vague assertion accepts many wrong answers.
- **Order, when order is promised.** If a docstring says "sorted
  alphabetically", test with items added in a different order, or a mutant
  that forgets to sort will pass.
- **One behaviour per test**, named after the behaviour
  (`test_remove_exact_stock_forgets_item`), so a failure tells you what broke
  before you even read the test.

To see the idea in action, imagine a mutant of `low_stock` with `<=` changed
to `<`. With apple at 5 and pear at 1, `low_stock(2)` is `["pear"]` for both
versions, so that test cannot tell them apart. `low_stock(1)` can: the real
code returns `["pear"]` (1 is less than or equal to 1), the mutant returns
`[]`. One test at exactly the boundary kills the mutant.

## Your turn

Read the docstrings in `inventory.py` carefully: they are the specification,
and every sentence in them is a rule some mutant breaks. Write tests in
`test_inventory.py` so that:

1. they all pass against the real `inventory.py`, and
2. every hidden mutant makes at least one of them fail.

Write at least five test functions (a check counts the `def test_` lines).
You can, and should, replace the weak starter test. Do not change
`inventory.py`: the grader runs your tests against its own copy, so changes
there have no effect. Use **Run** to run your tests against the real code;
**Check** reports which mutants survived, with a one-line description of each
one's bug, so you know which rule you have not tested yet.
