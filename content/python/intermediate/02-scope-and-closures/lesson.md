---
title: Scope and closures
summary: How Python finds a name, nonlocal, and functions that remember their surroundings.
order: 2
files: [closures.py]
run: python -i closures.py
hints:
  - "`make_counter`: define `count = 0`, then an inner `def increment(): nonlocal count; count += 1; return count`, and return `increment`."
  - "`make_multiplier(n)` returns `lambda x: x * n`. The lambda remembers `n`."
  - "`make_accumulator`: keep a list outside the inner function; appending to it needs no `nonlocal` because you never reassign the name."
  - "`make_adders`: the loop-variable trap. Bind the current value with a default argument, `lambda x, i=i: x + i`."
---

## Where Python looks for a name: LEGB

When code uses a name, Python searches four scopes in order:

1. **L**ocal: inside the current function
2. **E**nclosing: inside any function that contains this one
3. **G**lobal: the module's top level
4. **B**uilt-in: `len`, `print`, `range`...

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        return x          # finds the enclosing x
    return inner()
```

## Assigning makes a name local

Assigning to a name anywhere in a function makes it local for the **whole**
function, which gives this confusing error:

```python
count = 0
def bump():
    count += 1        # UnboundLocalError: count is local, but not yet set
```

`global count` would fix it, but module-level state changed from inside
functions is hard to follow. There is almost always a better design.

## nonlocal

`nonlocal` lets an inner function reassign a variable in an enclosing function:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c = make_counter()
c(), c(), c()        # 1, 2, 3
d = make_counter()
d()                  # 1: each call to make_counter has its own count
```

You only need `nonlocal` to **reassign**. Mutating an object the name refers
to (`items.append(x)`) works without it.

## Closures

`increment` above is a **closure**: a function bundled with the variables it
uses from where it was defined. The variables stay alive as long as the
closure does, even after `make_counter` has returned.

Closures are a lightweight alternative to a class with one method:

```python
def make_greeter(greeting):
    def greet(name):
        return f"{greeting}, {name}!"
    return greet

hello = make_greeter("Hello")
hello("Ana")      # 'Hello, Ana!'
```

## The late-binding trap

A closure captures the **variable**, not its value at the time:

```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]      # [2, 2, 2], not [0, 1, 2]
```

All three lambdas look up `i` when they are **called**, and by then the loop
has finished with `i == 2`. Capture the current value with a default argument:

```python
funcs = [lambda i=i: i for i in range(3)]
[f() for f in funcs]      # [0, 1, 2]
```

## Your turn

In `closures.py`:

- `make_counter(start=0)`: returns a function; each call returns the next
  number, starting at `start + 1`
- `make_multiplier(n)`: returns a function that multiplies its argument by `n`
- `make_accumulator()`: returns a function `add(x)` that remembers every value
  it was given and returns the running average
- `make_adders(n)`: a list of `n` functions where the one at index `i` adds `i`
  to its argument
