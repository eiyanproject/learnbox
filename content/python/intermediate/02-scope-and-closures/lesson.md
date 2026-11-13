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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **scope** | the region of a program where a name can be seen |
| **LEGB** | the order Python searches for a name: Local, Enclosing, Global, Built-in |
| **local scope** | inside the current function |
| **enclosing scope** | inside a function that contains this one |
| **global scope** | the module's top level |
| **built-in scope** | names Python always has: `len`, `print`, `range` |
| **module** | one Python file; its top level is the global scope |
| **shadow** | an inner name hiding an outer one of the same name |
| **unbound** | has no value yet |
| **state** | data a program keeps and changes over time |
| **reassign** | point a name at a new value (`=`, `+=`); needs `nonlocal` or `global` for an outer name |
| **mutate** | change the object a name points at (`items.append(x)`); needs no `nonlocal` |
| **inner function** | a function defined inside another |
| **closure** | a function bundled with the variables it uses from where it was defined, kept alive after the outer function returns |
| **late binding** | a closure looks a name up when it is **called**, not when it is made |
| **default-argument capture** | `lambda i=i: i` freezes the current value, because defaults are worked out once |
| **average** | the total of the values divided by how many there are |

### Python keywords

| Name | What it does |
|---|---|
| `global name` | in a function, makes `name` mean the module-level variable |
| `nonlocal name` | in an inner function, makes `name` mean the enclosing function's variable |
| `return inner` | returns the inner function itself (no brackets, so it is not called) |
| `lambda x: x * n` | a small function; it remembers `n` from where it was made |
| `+=` | counts as an assignment, so it makes the name local |

### Errors

| Error | Means |
|---|---|
| `UnboundLocalError` | a local variable was read before it was given a value, typically `count += 1` on a global without `global` |

---

A name's **scope** is the region of a program where that name can be seen.
A variable created inside a function exists only inside that function, so two
functions can each have their own `total` without interfering. This lesson is
about exactly how Python decides which variable a name refers to, and about a
powerful thing that falls out of the rules: functions that remember values
from the place where they were created.

## Where Python looks for a name: LEGB

When code uses a name, Python searches four scopes in order, and uses the
first one where the name exists:

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

There are three different variables called `x` here. `inner` has no `x` of
its own (no local), so Python looks in the enclosing function, `outer`, finds
`x = "enclosing"` there, and stops. The global `x` is never reached. When an
inner name hides an outer one like this, the inner one is said to
**shadow** it.

The built-in scope is why `len` and `print` work everywhere without being
imported. It is also why naming your own variable `list` or `str` is a bad
idea: your global `list` would shadow the built-in one, and `list(...)` would
stop working in that module.

## Assigning makes a name local

Reading a global variable from inside a function works fine. Assigning to
one does not do what you might expect. When Python reads a function's
definition, before running any of it, any name that is assigned to anywhere
in its body (with `=`, `+=`, as a loop
variable, and so on) is treated as local for the **whole** function, even on
lines before the assignment. That gives this confusing error:

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

`count += 1` means `count = count + 1`, so it is an assignment, so `count`
is local to `bump`. The right-hand side then tries to read the *local*
`count`, which has not been given a value yet, and Python stops with
`UnboundLocalError` ("unbound" means "has no value"). The global `count = 0`
is never even considered.

Writing `global count` as the first line of `bump` would fix it: it tells
Python that `count` in this function means the module-level variable. But
module-level state changed from inside functions is hard to follow, because
any function anywhere might be the one that changed it. There is almost
always a better design: pass the value in as an argument and return the new
one, or keep the state in an object.

## nonlocal

`nonlocal` is the same idea one level in: it lets an inner function reassign
a variable that belongs to the function enclosing it, instead of creating a
new local one:

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

`make_counter` does not return a number; it returns the `increment` function
itself (no brackets, so it is not called). `c` is now that function, and each
`c()` adds one to `count` and returns it. Without `nonlocal`, `count += 1`
would make a new local `count` inside `increment` and fail exactly as `bump`
did.

You only need `nonlocal` to **reassign** a name. Mutating an object the name
refers to, such as `items.append(x)`, does not assign to `items`; it changes
the list `items` already points at. So it works without `nonlocal`:

```pycon
>>> def make_log():
...     items = []
...     def log(x):
...         items.append(x)      # no assignment to items, no nonlocal needed
...         return items
...     return log
...
>>> log = make_log()
>>> log("a")
['a']
>>> log("b")
['a', 'b']
```

## Closures

`increment` above is a **closure**: a function bundled with the variables it
uses from where it was defined. Normally a function's local variables vanish
when it returns. Here, though, `increment` still needs `count`, so Python
keeps `count` alive for as long as `increment` exists, even after
`make_counter` has returned. Each call of `make_counter` creates a new
`count` and a new `increment` that uses it, which is why `d` started again
from 1 instead of carrying on from `c`'s 3.

Closures are a lightweight alternative to a class with one method. The
outer function's arguments play the part of `__init__`, and the inner
function is the method:

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

A closure captures the **variable**, not the value it held at the time the
function was created. Usually the difference does not show, but in a loop it
does:

```pycon
>>> funcs = [lambda: i for i in range(3)]
>>> [f() for f in funcs]      # not [0, 1, 2]
[2, 2, 2]
```

The comprehension creates three separate lambdas, but they all refer to the
same single variable `i`. None of them looks at `i` until it is **called**,
and by then the loop has finished, leaving `i` at its last value, 2. So all
three return 2. This is called **late binding**: the name is looked up late,
at call time.

The usual fix is to capture the current value with a default argument:

```pycon
>>> funcs = [lambda i=i: i for i in range(3)]
>>> [f() for f in funcs]
[0, 1, 2]
```

`i=i` looks odd, but it reads as "a parameter called `i`, whose default is
the current value of the loop's `i`". This uses the rule from the previous
lesson that made mutable defaults a trap: a default is worked out once, when
the function is created. Here that is exactly what we want, so each lambda
gets its own copy of the value at the moment it was made.

## Your turn

In `closures.py`, every function returns a function (or a list of them):

- `make_counter(start=0)`: each call of the returned function gives the next
  number after `start`. With `count = make_counter(5)`, the first `count()`
  is `6` and the second is `7`.
- `make_multiplier(n)`: the returned function multiplies its argument by `n`:
  `make_multiplier(3)(5)` is `15`
- `make_accumulator()`: the returned function `add(x)` remembers every value
  it has been given, across calls, and returns the average of all of them so
  far. With
  `add = make_accumulator()`, `add(10)` is `10.0`, then `add(20)` is `15.0`,
  then `add(60)` is `30.0`.
- `make_adders(n)`: a list of `n` functions, where the one at index `i` adds
  `i` to its argument. Calling each function of `make_adders(3)` with `10`
  gives `10`, `11` and `12`. This is the late-binding trap from above: the
  obvious version gives `12`, `12`, `12`.
