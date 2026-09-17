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

A **list** holds items in order, and can change:

```python
scores = [72, 88, 95]
scores.append(60)        # [72, 88, 95, 60]
scores.insert(0, 100)    # [100, 72, 88, 95, 60]
scores.remove(88)        # removes the first 88
last = scores.pop()      # removes and returns the last item (60)
scores[0] = 99           # replace by position
len(scores)              # 4
```

Indexing and slicing work exactly as they do on strings: `scores[0]`,
`scores[-1]`, `scores[1:3]`, `scores[::-1]`.

## Useful built-ins

```python
nums = [5, 2, 9, 1]
sum(nums)          # 17
min(nums)          # 1
max(nums)          # 9
sorted(nums)       # [1, 2, 5, 9]  a NEW list; nums is unchanged
nums.sort()        # sorts nums itself, returns None
sorted(nums, reverse=True)
sorted(["bb", "a", "ccc"], key=len)   # ['a', 'bb', 'ccc']
9 in nums          # True
nums.index(9)      # position of 9
nums.count(2)      # how many 2s
```

## Two names, one list

Assignment does not copy a list. Both names point at the same object:

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)       # [1, 2, 3, 4]  a changed too

c = a.copy()   # or a[:] or list(a): a real, separate copy
```

This matters for functions. A function that calls `.append()` or `.sort()`
on a list it was given changes the caller's list. Unless that is the point of
the function, work on a copy or build a new list.

## Tuples

A **tuple** is like a list that cannot change. Use one for a small, fixed
group of values that belong together:

```python
point = (3, 4)
x, y = point            # unpacking
rgb = (255, 180, 84)
```

You have already used tuples: `return a, b` returns one.

## Lists of lists

```python
grid = [
    [1, 2, 3],
    [4, 5, 6],
]
grid[1][2]    # 6
```

## zip

Walk two lists side by side:

```python
names = ["Ana", "Budi"]
ages = [31, 27]
for name, age in zip(names, ages):
    print(name, age)
```

## Your turn

In `lists.py`, write these without changing the list you are given:

- `second_largest(numbers)`: the second largest **distinct** value, or `None`
  if there is none: `[4, 9, 9, 2]` gives `4`
- `chunk(items, size)`: split into lists of `size`; the last may be shorter:
  `chunk([1, 2, 3, 4, 5], 2)` gives `[[1, 2], [3, 4], [5]]`
- `rotate(items, k)`: move every item `k` places to the right, wrapping round:
  `rotate([1, 2, 3, 4, 5], 2)` gives `[4, 5, 1, 2, 3]`
- `bounding_box(points)`: given `(x, y)` tuples, return
  `((min_x, min_y), (max_x, max_y))`
