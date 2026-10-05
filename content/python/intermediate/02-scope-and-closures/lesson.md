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

```pycon
>>> x = "global"
>>> def outer():
...     x = "enclosing"
...     def inner():
...         return x          # finds the enclosing x
...     return inner()
...
>>> outer()
'enclosing'
```

## Assigning makes a name local

Assigning to a name anywhere in a function makes it local for the **whole**
function, which gives this confusing error:

```pycon
>>> count = 0
>>> def bump():
...     count += 1        # makes count local to bump - but it has no value yet
...
>>> bump()
Traceback (most recent call last):
  ...
UnboundLocalError: cannot access local variable 'count'...
```

`global count` would fix it, but module-level state changed from inside
functions is hard to follow. There is almost always a better design.

## nonlocal

`nonlocal` lets an inner function reassign a variable in an enclosing function:

```pycon
>>> def make_counter():
...     count = 0
...     def increment():
...         nonlocal count
...         count += 1
...         return count
...     return increment
...
>>> c = make_counter()
>>> c(), c(), c()
(1, 2, 3)
>>> d = make_counter()
>>> d()                  # each call to make_counter has its own count
1
```

You only need `nonlocal` to **reassign**. Mutating an object the name refers
to (`items.append(x)`) works without it.

## Closures

`increment` above is a **closure**: a function bundled with the variables it
uses from where it was defined. The variables stay alive as long as the
closure does, even after `make_counter` has returned.

Closures are a lightweight alternative to a class with one method:

```pycon
>>> def make_greeter(greeting):
...     def greet(name):
...         return f"{greeting}, {name}!"
...     return greet
...
>>> hello = make_greeter("Hello")
>>> hello("Ana")
'Hello, Ana!'
```

## The late-binding trap

A closure captures the **variable**, not its value at the time:

```pycon
>>> funcs = [lambda: i for i in range(3)]
>>> [f() for f in funcs]      # not [0, 1, 2]
[2, 2, 2]
```

All three lambdas look up `i` when they are **called**, and by then the loop
has finished with `i == 2`. Capture the current value with a default argument:

```pycon
>>> funcs = [lambda i=i: i for i in range(3)]
>>> [f() for f in funcs]
[0, 1, 2]
```

## Your turn

In `closures.py`, every function returns a function (or a list of them):

- `make_counter(start=0)`: each call of the returned function gives the next
  number after `start`. With `count = make_counter(5)`, the first `count()`
  is `6` and the second is `7`.
- `make_multiplier(n)`: the returned function multiplies its argument by `n`:
  `make_multiplier(3)(5)` is `15`
- `make_accumulator()`: the returned function `add(x)` remembers every value
  it has been given and returns their average so far. With
  `add = make_accumulator()`, `add(10)` is `10.0`, then `add(20)` is `15.0`,
  then `add(60)` is `30.0`.
- `make_adders(n)`: a list of `n` functions, where the one at index `i` adds
  `i` to its argument. Calling each function of `make_adders(3)` with `10`
  gives `10`, `11` and `12`.
