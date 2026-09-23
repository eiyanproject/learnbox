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
  - "`apply_all` just feeds the value through each function in turn: start with `value`, reassign it in a loop."
---

The syllabus calls this section "more control flow tools" and gives it **nine**
of the forty questions — more than any other. Most of them turn on behaviour
that only shows up in an edge case.

## Loops have an else

```python
for item in values:
    if matches(item):
        break
else:
    print("nothing matched")
```

The `else` runs when the loop **finishes without breaking**. It is the cleanest
way to express "I searched everything and found nothing", and it is a reliable
exam question because most people expect `else` to pair with `if`.

`while` loops take an `else` too, with the same rule.

## Default arguments are evaluated once

```python
def broken(item, target=[]):    # evaluated at definition time
    target.append(item)
    return target

broken(1)       # [1]
broken(2)       # [1, 2]   - the same list, still there
```

This is the single most asked-about trap in the language. The fix is always the
same shape:

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

Calling with `f(*[1, 2])` and `f(**{"a": 1})` unpacks in the other direction.

## Lambdas and annotations

`lambda x: x * 2` is one expression, no statements, no `return`. Annotations
(`def f(x: int) -> str:`) are **not** enforced at runtime; they are stored in
`f.__annotations__` and that is all Python does with them.

## Your turn

In `flow.py`:

- `first_divisible(values, divisor)`: the first value divisible by `divisor`,
  or the string `"none"` if there is none — written with `for ... else`
- `append_safely(item, target=None)`: appends and returns the list, without the
  shared-default bug
- `describe_args(*args, **kwargs)`: a dict with keys `count` (how many
  positional), `names` (sorted keyword names) and `total` (sum of the
  positional arguments)
- `apply_all(funcs, value)`: feed `value` through each function in order and
  return the final result
