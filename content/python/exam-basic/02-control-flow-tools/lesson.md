---
title: "Paper 2: control flow and functions"
summary: Loop else, the mutable default argument, *args and **kwargs, lambdas and annotations - the heaviest section of the exam.
order: 2
files: [flow.py]
run: python -i flow.py
hints:
  - "`for ... else` runs the `else` only when the loop finished without `break`. Put the `return` inside the loop and the fallback in the `else`."
  - "A default argument is evaluated **once**, when the function is defined. The fix is `target=None`, then `if target is None: target = []` inside the body."
  - "`*args` collects extra positional arguments into a tuple, `**kwargs` collects extra keyword arguments into a dict. The order in a signature is positional, `*args`, keyword-only, `**kwargs`."
  - "`apply_all` feeds the value through each function in turn: start with `value`, reassign it in a loop."
---

The syllabus calls this section "more control flow tools" and gives it **nine**
of the forty questions — more than any other. Most of them turn on behaviour
that only shows up in an edge case.

## Loops have an else

```python
values = [1, 3, 5]
for item in values:
    if item % 2 == 0:         # looking for an even number
        break
else:
    print("nothing matched")  # the loop ran out without a break
```

```output
nothing matched
```

The `else` runs when the loop **finishes without breaking**. It is the cleanest
way to express "I searched everything and found nothing", and it is a reliable
exam question because most people expect `else` to pair with `if`. Note the
indentation above: the `else` lines up with the `for`, not with the `if`
inside it.

With an even number in the list, the `break` happens, and the `else` is
skipped:

```python
for item in [1, 4, 5]:
    if item % 2 == 0:
        print("found", item)
        break
else:
    print("nothing matched")
```

```output
found 4
```

An empty list never breaks, so its loop's `else` always runs. Think of the
`else` as "no break".

`while` loops take an `else` too, with the same rule: it runs when the
condition becomes false, and not when the loop is left by `break`.

## Default arguments are evaluated once

```pycon
>>> def broken(item, target=[]):    # evaluated at definition time
...     target.append(item)
...     return target
...
>>> broken(1)
[1]
>>> broken(2)       # the same list, still there
[1, 2]
```

The `def` line runs once, and the `[]` in it is created then, once. Every call
that leaves `target` out gets that one list, so items pile up across calls.
This is the single most asked-about trap in the language. The fix is always
the same shape: use `None` as the default, and create the list inside the
body, which runs on every call:

```python
def fixed(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

## Argument forms

```python
def f(a, b=2, *args, key=None, **kwargs): ...
```

| Form | Collects | Type inside |
| --- | --- | --- |
| `b=2` | a default | whatever was passed |
| `*args` | extra positional | `tuple` |
| `key=None` | keyword-only, after `*args` | whatever was passed |
| `**kwargs` | extra keyword | `dict` |

Seeing where each argument lands is the quickest way to learn the table:

```pycon
>>> def f(a, b=2, *args, key=None, **kwargs):
...     return a, b, args, key, kwargs
...
>>> f(1)
(1, 2, (), None, {})
>>> f(1, 5, 6, 7, key="k", extra=True)
(1, 5, (6, 7), 'k', {'extra': True})
```

`a` and `b` take the first two positional values; `*args` takes the rest as
a tuple; `key` can only be given by name, because it comes after `*args`;
and any other keyword goes into `kwargs` as a dict.

Calling with `f(*[1, 2])` and `f(**{"a": 1})` unpacks in the other direction:
`*` spreads a list or tuple out as positional arguments, and `**` spreads a
dict out as keyword arguments:

```pycon
>>> f(*[1, 2])            # the same as f(1, 2)
(1, 2, (), None, {})
>>> f(**{"a": 1, "key": "x"})   # the same as f(a=1, key="x")
(1, 2, (), 'x', {})
```

## Lambdas and annotations

`lambda x: x * 2` is one expression, no statements, no `return`: the value
of the expression is what the lambda returns. It is the same as a `def` with
a one-line `return`, but has no name of its own.

Annotations (`def f(x: int) -> str:`) are **not** enforced at runtime; they
are stored in `f.__annotations__` and that is all Python does with them:

```pycon
>>> double = lambda x: x * 2
>>> double(4)
8
>>> def label(x: int) -> str:
...     return f"#{x}"
...
>>> label("not an int")          # no error: annotations are not checked
'#not an int'
>>> label.__annotations__
{'x': <class 'int'>, 'return': <class 'str'>}
```

## Your turn

In `flow.py`:

- `first_divisible(values, divisor)`: the first value that `divisor` divides
  exactly (no remainder), or the string `"none"` if there is no such value -
  written with `for ... else`. `first_divisible([3, 8, 10], 4)` is `8`, and
  `first_divisible([3, 5], 4)` and `first_divisible([], 4)` are `"none"`.
- `append_safely(item, target=None)`: append `item` to the list `target` and
  return the list. Called without a list, it starts a new empty one every
  time, without the shared-default bug: `append_safely(1)` is `[1]`, and so is
  the next `append_safely(1)`. `append_safely(2, [1])` is `[1, 2]`.
- `describe_args(*args, **kwargs)`: a dict with three keys: `count`, how many
  positional arguments there were; `names`, the keyword names as a sorted
  list; and `total`, the sum of the positional arguments.
  `describe_args(1, 2, b=0, a=0)` is
  `{"count": 2, "names": ["a", "b"], "total": 3}`. With no positional
  arguments, `count` and `total` are `0`; with no keywords, `names` is `[]`.
- `apply_all(funcs, value)`: a pipeline. Call the first function with
  `value`, the second with what the first returned, and so on, and return
  what the last one returns. `apply_all([abs, str], -3)` is `"3"`: `abs`
  gives `3`, then `str` gives `"3"`. With no functions it returns `value`.
