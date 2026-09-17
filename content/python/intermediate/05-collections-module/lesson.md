---
title: The collections toolbox
summary: Counter, defaultdict, deque and namedtuple, plus heapq and bisect for ordered data.
order: 5
files: [toolbox.py]
run: python -i toolbox.py
hints:
  - "`top_words`: `Counter(words).most_common(n)` already returns `(word, count)` pairs in the right order."
  - "`index_by_tag`: `defaultdict(list)`, then `index[tag].append(name)`. Return `dict(index)`."
  - "`moving_average`: `deque(maxlen=window)` drops the oldest value by itself; yield `sum(d) / len(d)` once it is full."
  - "`k_smallest` is `heapq.nsmallest(k, items)`. `grade_for` uses `bisect.bisect(breakpoints, score)` as an index into the grades string."
---

The built-in `list`, `dict` and `set` cover most needs. The `collections`
module fills the gaps, and each tool replaces a pattern you would otherwise
write by hand.

## Counter

```python
from collections import Counter

c = Counter("mississippi")
c["s"]              # 4
c["z"]              # 0: missing keys count as zero, no KeyError
c.most_common(2)    # [('i', 4), ('s', 4)]
c.update("sss")     # add more counts
Counter(a=3) + Counter(a=1, b=2)   # Counter({'a': 4, 'b': 2})
```

## defaultdict

A dict that creates a default value for a missing key on first access:

```python
from collections import defaultdict

groups = defaultdict(list)
for name, team in [("ana", "red"), ("budi", "blue"), ("citra", "red")]:
    groups[team].append(name)
# {'red': ['ana', 'citra'], 'blue': ['budi']}
```

The argument is a function that makes the default: `list`, `int`, `set`,
or `lambda: "unknown"`. Convert with `dict(groups)` before handing it to code
that should not auto-create keys.

## deque

A double-ended queue: fast appends and pops at **both** ends (a list is slow
at the front):

```python
from collections import deque

q = deque([1, 2, 3])
q.appendleft(0)
q.popleft()
q.rotate(1)

recent = deque(maxlen=3)       # keeps only the last 3 items
for x in range(10):
    recent.append(x)
list(recent)                   # [7, 8, 9]
```

## namedtuple

A tuple with named fields: readable, immutable and lightweight:

```python
from collections import namedtuple

Point = namedtuple("Point", "x y")
p = Point(3, 4)
p.x, p[1]            # 3, 4
p._replace(x=10)     # Point(x=10, y=4)
```

(`dataclasses`, next lesson, are the more flexible option.)

## heapq: always know the smallest

A heap is a list kept in an order where `heap[0]` is always the smallest item.
Pushing and popping are fast even for huge lists:

```python
import heapq

heap = []
for n in [5, 1, 8, 3]:
    heapq.heappush(heap, n)
heapq.heappop(heap)             # 1
heapq.nsmallest(2, [5, 1, 8])   # [1, 5]
heapq.nlargest(2, data, key=len)
```

Push `(priority, item)` tuples to build a priority queue.

## bisect: searching sorted lists

```python
import bisect

scores = [60, 70, 80, 90]
bisect.bisect(scores, 75)       # 2: position where 75 would be inserted
bisect.insort(scores, 85)       # insert keeping the list sorted
```

## Your turn

In `toolbox.py`:

- `top_words(text, n)`: the `n` most common lower-cased words as `(word, count)` pairs
- `index_by_tag(items)`: `items` are `(name, [tags])`; return a plain `dict`
  from tag to the names that have it, in order
- `moving_average(values, window)`: a generator of the average of each full
  window of consecutive values
- `k_smallest(items, k)`: the `k` smallest items, sorted
- `grade_for(score)`: `"F"` below 60, `"D"` from 60, `"C"` from 70, `"B"` from 80,
  `"A"` from 90, using `bisect`
