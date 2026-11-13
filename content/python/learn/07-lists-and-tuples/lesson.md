---
title: Lists and tuples
summary: Ordered collections you can grow, sort and slice, and the fixed-size tuple.
order: 7
files: [lists.py]
run: python -i lists.py
hints:
  - "`sorted()` returns a new list; `.sort()` changes the list in place and returns `None`. The task asks you not to change the input, so use `sorted()` or a copy."
  - "`second_largest`: remove duplicates with `set(numbers)`, sort, and take `[-2]`. Check the length first."
  - "`chunk(items, size)`: `range(0, len(items), size)` gives the start of each chunk; slice `items[start:start + size]`."
  - "`rotate(items, k)`: `k = k % len(items)` handles large k. Then `items[-k:] + items[:-k]` rotates right. Watch out for an empty list and for `k == 0`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **list** | items in a fixed order, in square brackets; it can be changed after it is made |
| **item** | one value in a list |
| **object** | a value in memory; changing a list updates the same object |
| **by value** / **by position** | find an item by what it is (`remove(88)`) / by where it is (`pop(0)`) |
| **built-in** | a function Python always has, without importing: `sum`, `len`, `sorted` |
| **in place** | changing the list itself rather than making a new one |
| **key function** | a function applied to each item to decide its order: `key=len` |
| **alias** | a second name for the same list; `b = a` does not copy |
| **copy** | a real, separate list: `a.copy()`, `a[:]` or `list(a)` |
| **tuple** | like a list that cannot change, in round brackets: `(3, 4)` |
| **unpacking** | giving each item its own name: `x, y = point` |
| **swap** | exchange two values: `a, b = b, a` |
| **trailing comma** | the comma in `(5,)`, which makes a one-item tuple |
| **list of lists** | a list whose items are lists, like rows of a table: `grid[1][2]` |
| **distinct** | different from each other; equal values count once |
| **set** | a collection with one of each value (the next lesson) |
| **rotate** | move items along, with the ones pushed off one end coming back at the other |
| **bounding box** | the smallest and largest x and y of a group of points |

### Python methods and functions

| Name | What it does |
|---|---|
| `items.append(x)` | adds `x` at the end |
| `items.insert(i, x)` | puts `x` at position `i`, moving the rest along |
| `items.remove(x)` | removes the first item equal to `x` (an error if absent) |
| `items.pop()`, `items.pop(i)` | removes and returns the last item; the item at `i` |
| `items[i] = x` | replaces the item at position `i` |
| `len(items)` | the number of items |
| `sum`, `min`, `max` | total; smallest; largest |
| `sorted(items)` | a **new** sorted list; the original is unchanged |
| `items.sort()` | sorts the list itself and returns `None` |
| `reverse=True` | sort largest first |
| `x in items` | `True` if `x` is in the list |
| `items.index(x)` | the position of the first `x` |
| `items.count(x)` | how many times `x` appears |
| `items.copy()` | a separate copy |
| `zip(a, b)` | walks lists side by side, giving tuples of items at the same position; stops at the shortest |
| `set(items)` | one of each value |
| `range(0, len(items), size)` | the start of each chunk |
| `%` | remainder: `k % len(items)` |

### Errors

| Error | Means |
|---|---|
| `TypeError` | the operation is not allowed, such as changing a tuple: `point[0] = 5` |
| `ValueError` | `remove` or `index` with a value that is not in the list |
| `ZeroDivisionError` | `% 0` or `/ 0`: dividing by zero, as when rotating an empty list |

---

A **list** holds several values, called **items**, in a fixed order. You
write one with square brackets and commas between the items. Unlike a
string, a list can be changed after it is made: you can add, remove and
replace items, and the same list object is updated rather than a new one
being built. The items can be of any type, and one list can even mix types,
though in practice a list usually holds one kind of thing.

```pycon
>>> scores = [72, 88, 95]
>>> scores.append(60)
>>> scores
[72, 88, 95, 60]
>>> scores.insert(0, 100)    # at position 0
>>> scores
[100, 72, 88, 95, 60]
>>> scores.remove(88)        # removes the first 88
>>> scores.pop()             # removes and returns the last item
60
>>> scores[0] = 99           # replace by position
>>> scores
[99, 72, 95]
>>> len(scores)
3
```

Step by step: `append` added 60 at the end. `insert(0, 100)` put 100 at
position 0 and moved everything else one place along. `remove(88)` searched
for the value 88 and took out the first one it found (it is an error if the
value is not there). `pop()` took the last item off and handed it back, which
is why 60 appears. Finally `scores[0] = 99` replaced the item at position 0.

Note the difference: `remove` works by **value** ("take out the 88"), while
`pop` and `scores[0] = ...` work by **position**. `pop(0)` would remove the
first item instead of the last.

Indexing and slicing work exactly as they do on strings: `scores[0]`,
`scores[-1]`, `scores[1:3]`, `scores[::-1]`. A slice of a list is a new list.

## Useful built-ins

```pycon
>>> nums = [5, 2, 9, 1]
>>> sum(nums)
17
>>> min(nums)
1
>>> max(nums)
9
>>> sorted(nums)       # a NEW list...
[1, 2, 5, 9]
>>> nums               # ...and nums is unchanged
[5, 2, 9, 1]
>>> nums.sort()        # sorts nums itself, and returns None
>>> nums
[1, 2, 5, 9]
>>> sorted(nums, reverse=True)
[9, 5, 2, 1]
>>> sorted(["bb", "a", "ccc"], key=len)    # sort by length
['a', 'bb', 'ccc']
>>> 9 in nums
True
>>> nums.index(9)      # the position of 9
3
>>> nums.count(2)      # how many 2s
1
```

The most important pair here is `sorted()` and `.sort()`. They give the
same order but behave very differently:

- `sorted(nums)` is a function. It leaves `nums` alone and returns a brand
  new sorted list.
- `nums.sort()` is a method. It rearranges `nums` itself and returns `None`.
  So `nums = nums.sort()` is a classic bug: the list is sorted, then the name
  is pointed at `None`.

Both accept `reverse=True` for largest first, and `key=`, a function that is
applied to each item to decide its place. `key=len` sorts by length instead of
alphabetically. Note that the function is passed by its name, `len`, without
brackets: you are handing `sorted` the function itself to use, not calling it.

## Two names, one list

Assignment does not copy a list. A variable is a name pointing at a value,
so `b = a` makes a second name that points at the very same list. Change the
list through either name and both see the change:

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)       # a changed too

c = a.copy()   # or a[:] or list(a): a real, separate copy
c.append(5)
print(a, c)    # this time only the copy changed
```

```output
[1, 2, 3, 4]
[1, 2, 3, 4] [1, 2, 3, 4, 5]
```

This never comes up with numbers or strings, because those cannot be changed
in place; any "change" makes a new value. It comes up with lists because
`append`, `sort` and the rest really do change the list object.

It matters for functions too. Passing a list to a function does not copy it:
the parameter is one more name for the caller's list. A function that calls
`.append()` or `.sort()` on a list it was given changes the caller's list.
Unless that is the point of the function, work on a copy or build a new list,
and leave the original as you found it.

## Tuples

A **tuple** is like a list that cannot change: once it is made, you cannot
add, remove or replace its items. It is written with round brackets instead
of square ones. Use one for a small, fixed group of values that belong
together, where each position has its own meaning, like an x and a y:

```python
point = (3, 4)
x, y = point            # unpacking
rgb = (255, 180, 84)
print(x, y)
print(rgb[0])
```

```output
3 4
255
```

**Unpacking** assigns each item of the tuple to its own name, in order, so
here `x` is 3 and `y` is 4. The number of names must match the number of
items. Unpacking works on lists too, and it gives a neat way to swap two
variables:

```pycon
>>> a, b = 1, 2
>>> a, b = b, a
>>> a, b
(2, 1)
```

You read a tuple the same way as a list (`point[0]`, slicing, `len`, `in`),
but `point[0] = 5` is an error. A tuple of one item needs a trailing comma,
`(5,)`, because `(5)` is the number 5 in ordinary maths brackets:

```pycon
>>> point = (3, 4)
>>> point[0] = 5
Traceback (most recent call last):
  ...
TypeError: 'tuple' object does not support item assignment
>>> type((5)), type((5,))
(<class 'int'>, <class 'tuple'>)
```

You have already used tuples: `return a, b` returns one.

When should you use which? A list is for a varying number of the same kind
of thing (all the scores, all the users). A tuple is for a fixed number of
values that form one thing together (a point, a date, an RGB colour).

## Lists of lists

A list can hold other lists, which is a simple way to store a table or a
grid. The first index picks the row, and a second index picks the item
within that row:

```pycon
>>> grid = [
...     [1, 2, 3],
...     [4, 5, 6],
... ]
>>> grid[1]       # the second row
[4, 5, 6]
>>> grid[1][2]    # the third item of the second row
6
```

`grid[1][2]` is worked out from left to right: `grid[1]` is the row
`[4, 5, 6]`, and `[2]` of that row is `6`.

## zip

`zip()` walks two (or more) lists side by side. Each time round it gives you
a tuple with one item from each list, taken from the same position, which
you unpack into two names. It stops as soon as the shortest list runs out:

```python
names = ["Ana", "Budi"]
ages = [31, 27]
for name, age in zip(names, ages):
    print(name, age)
```

```output
Ana 31
Budi 27
```

## Your turn

In `lists.py`, write these without changing the list you are given. Some of
the tests check that the original list is the same afterwards, so return a
new list rather than sorting or editing the input:

- `second_largest(numbers)`: the second largest **distinct** value, or `None`
  if there is none. Equal numbers count once: `[4, 9, 9, 2]` gives `4`, not
  `9`, and `[7, 7]` gives `None`. (`set(numbers)`, from the next lesson,
  keeps one of each value; `sorted()` accepts a set and returns a list.)
- `chunk(items, size)`: split the list into smaller lists of `size` items
  each, in order; the last one may be shorter if the items do not divide
  evenly: `chunk([1, 2, 3, 4, 5], 2)` gives `[[1, 2], [3, 4], [5]]`
- `rotate(items, k)`: move every item `k` places to the right. Items pushed
  off the right-hand end come back in at the left:
  `rotate([1, 2, 3, 4, 5], 2)` gives `[4, 5, 1, 2, 3]`. Rotating a list of 5
  by 5 brings it back to where it started, so a `k` larger than the list
  only matters by its remainder, `k % len(items)`. Rotating an empty list
  gives an empty list; handle that before the `%`, since `% 0` is a
  division by zero.
- `bounding_box(points)`: `points` is a list of `(x, y)` tuples. Return two
  tuples, `((min_x, min_y), (max_x, max_y))`: the smallest x and smallest y
  found anywhere in the list, then the largest of each.
  `bounding_box([(1, 5), (3, 2), (2, 8)])` gives `((1, 2), (3, 8))`. Neither
  corner has to be one of the points.
