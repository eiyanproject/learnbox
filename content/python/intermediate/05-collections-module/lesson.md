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

In the Beginner section you counted things with
`counts[word] = counts.get(word, 0) + 1` in a loop. A `Counter` does that in
one step: give it any iterable and it counts how many times each item
appears. It is a dict underneath, with the items as keys and the counts as
values, plus a few extra methods:

```pycon
>>> from collections import Counter
>>> c = Counter("mississippi")
>>> c["s"]
4
>>> c["z"]              # missing keys count as zero, no KeyError
0
>>> c.most_common(2)
[('i', 4), ('s', 4)]
>>> c.update("sss")     # add more counts
>>> c["s"]
7
>>> Counter(a=3) + Counter(a=1, b=2)
Counter({'a': 4, 'b': 2})
```

Line by line: a string is iterable, so `Counter("mississippi")` counts its
letters. Asking for a letter that never appeared gives 0 instead of a
`KeyError`, which is usually what you want from a count. `most_common(n)`
returns the `n` highest counts as `(item, count)` pairs, largest first; `i`
and `s` both appear 4 times, and on a tie the item seen first comes first.
`update()` adds counts from another iterable instead of replacing them. And
`+` adds two counters together, key by key.

## defaultdict

`defaultdict` is a dict that creates a value for a missing key the first
time you ask for it. It replaces the `setdefault` grouping pattern from the
Beginner section:

```python
from collections import defaultdict

groups = defaultdict(list)
for name, team in [("ana", "red"), ("budi", "blue"), ("citra", "red")]:
    groups[team].append(name)
print(dict(groups))
```

```output
{'red': ['ana', 'citra'], 'blue': ['budi']}
```

The argument is a function that makes the default, which `defaultdict`
calls with no arguments whenever a key is missing: `list` makes `[]`, `int`
makes `0`, `set` makes an empty set, and `lambda: "unknown"` makes the string
`"unknown"`. Pass the function itself, without brackets: `defaultdict(list)`,
not `defaultdict(list())`.

So the first time `groups["red"]` is used, there is no `"red"` key, an empty
list is created and stored under it, and `append` adds `"ana"` to it. The
second time, the list already exists and `"citra"` joins it.

The catch is that *any* lookup of a missing key creates it, even one that
only meant to check:

```pycon
>>> from collections import defaultdict
>>> d = defaultdict(list)
>>> d["typo"]              # only looking...
[]
>>> dict(d)                # ...but the key now exists
{'typo': []}
>>> "other" in d           # `in` is safe: it never creates keys
False
```

That is why the result is converted with `dict(groups)` before it is handed
to other code: a plain dict raises `KeyError` for a missing key, as the
caller would expect, instead of quietly growing.

## deque

A **deque** (pronounced "deck", short for double-ended queue) is a sequence
with fast appends and pops at **both** ends. A list is fast at the end but
slow at the front: `insert(0, x)` or `pop(0)` has to shift every other item
along by one place, which takes longer the bigger the list. A deque never
shifts anything, so it is the right type for a **queue**, where items join
at one end and leave from the other:

```pycon
>>> from collections import deque
>>> q = deque([1, 2, 3])
>>> q.appendleft(0)
>>> q
deque([0, 1, 2, 3])
>>> q.popleft()
0
>>> q.rotate(1)                # the last item moves to the front
>>> q
deque([3, 1, 2])
>>> recent = deque(maxlen=3)   # keeps only the last 3 items
>>> for x in range(10):
...     recent.append(x)
...
>>> list(recent)
[7, 8, 9]
```

`appendleft` and `popleft` are the front-end versions of `append` and
`pop`. `rotate(1)` moves every item one place to the right, wrapping the last
one round to the front (like the `rotate` exercise in the Beginner section).
With `maxlen`, the deque never grows past that size: appending to a full
deque silently drops an item from the other end. That makes "the last N
things" a one-liner.

## namedtuple

A **namedtuple** is a tuple whose positions also have names, so `p.x` can be
used instead of `p[0]`. It stays a real tuple, immutable and lightweight,
but reads far better:

```pycon
>>> from collections import namedtuple
>>> Point = namedtuple("Point", "x y")
>>> p = Point(3, 4)
>>> p.x, p[1]            # by name or by position
(3, 4)
>>> p._replace(x=10)     # a new tuple; p itself cannot change
Point(x=10, y=4)
```

`namedtuple("Point", "x y")` creates a new class called `Point` with two
fields, `x` and `y` (the field names are given in one string, separated by
spaces). Because tuples cannot change, `_replace` returns a new tuple with
one field swapped and leaves `p` as it was. The leading underscore is only
there so the method name cannot clash with a field you might call `replace`.

(`dataclasses`, next lesson, are the more flexible option.)

## heapq: always know the smallest

Sometimes you keep adding items and repeatedly need the smallest one: the
next task by priority, the earliest event. Sorting the list after every
addition works but is wasteful. A **heap** is a list kept in a special
partial order where `heap[0]` is always the smallest item, and the
`heapq` module's functions keep it that way as you push and pop. Pushing and
popping are fast even for huge lists:

```pycon
>>> import heapq
>>> heap = []
>>> for n in [5, 1, 8, 3]:
...     heapq.heappush(heap, n)
...
>>> heap[0]                      # the smallest, always
1
>>> heapq.heappop(heap)
1
>>> heap[0]                      # the next smallest moved up
3
>>> heapq.nsmallest(2, [5, 1, 8])
[1, 5]
>>> heapq.nlargest(2, ["fig", "banana", "kiwi"], key=len)
['banana', 'kiwi']
```

A heap is not a sorted list. Only `heap[0]` is guaranteed to be the
smallest; the rest are in an order that is only good enough to find the next
smallest quickly:

```pycon
>>> heap
[3, 5, 8]
>>> heapq.heappush(heap, 4)
>>> heap                         # 4 is not after 3 in sorted position...
[3, 4, 8, 5]
>>> heapq.heappop(heap), heapq.heappop(heap)   # ...but pops come out in order
(3, 4)
```

So always take items out with `heappop`, never by indexing past `[0]`.
`nsmallest` and `nlargest` are one-off helpers that need no heap of your
own: they return the `k` smallest or largest of any iterable, in order.

To build a **priority queue**, where the most urgent task comes out first,
push `(priority, item)` tuples. Tuples compare by their first item, so the
smallest priority number is always popped first:

```pycon
>>> tasks = []
>>> heapq.heappush(tasks, (2, "write report"))
>>> heapq.heappush(tasks, (1, "fix outage"))
>>> heapq.heappush(tasks, (3, "tidy desk"))
>>> heapq.heappop(tasks)
(1, 'fix outage')
```

## bisect: searching sorted lists

Finding where a value belongs in a sorted list does not need a loop over
every item. `bisect` repeatedly halves the part of the list it is searching,
so even in a list of a million items it needs only about twenty comparisons:

```pycon
>>> import bisect
>>> scores = [60, 70, 80, 90]
>>> bisect.bisect(scores, 75)       # the position where 75 would go
2
>>> bisect.insort(scores, 85)       # insert, keeping the list sorted
>>> scores
[60, 70, 80, 85, 90]
```

75 belongs between 70 (position 1) and 80 (position 2), so it would go in at
position 2. The list must already be sorted, or the answer is meaningless.

The returned position is useful in its own right: it tells you how many
values are less than or equal to yours. When the value is equal to one in
the list, `bisect` puts it **after** the equal one (`bisect_left` would put it
before):

```pycon
>>> bisect.bisect([60, 70, 80, 90], 70)
2
>>> bisect.bisect_left([60, 70, 80, 90], 70)
1
```

That "after" behaviour is what you want for grade boundaries like "70 and
above": a score of exactly 70 must land past the 70 mark.

## Your turn

In `toolbox.py`:

- `top_words(text, n)`: the `n` most common words, lower-cased, as
  `(word, count)` pairs, most common first:
  `top_words("The cat and the hat and the bat", 2)` is
  `[("the", 3), ("and", 2)]`. Split the text into words on whitespace. An
  empty text has no words, so it gives `[]`.
- `index_by_tag(items)`: each item is a `(name, tags)` pair, where `tags` is
  a list. Return a plain `dict` (not a `defaultdict`; a test checks the
  type) from each tag to the names that carry it, in the order they appear:
  `[("pen", ["blue", "small"]), ("sky", ["blue"])]` gives
  `{"blue": ["pen", "sky"], "small": ["pen"]}`
- `moving_average(values, window)`: a generator. Slide a window of `window`
  consecutive values along the list and yield the average of each position:
  `moving_average([1, 2, 3, 4], 2)` yields `1.5`, `2.5`, `3.5` (the averages
  of 1 and 2, of 2 and 3, of 3 and 4). A list shorter than the window yields
  nothing. It must be lazy: yield each average as soon as enough values have
  arrived, without reading the whole input first (a test checks this with a
  generator as input).
- `k_smallest(items, k)`: the `k` smallest items, sorted:
  `k_smallest([5, 1, 4, 2], 2)` is `[1, 2]`. If there are fewer than `k`
  items, return them all, sorted.
- `grade_for(score)`: `"F"` below 60, `"D"` from 60, `"C"` from 70, `"B"` from 80,
  `"A"` from 90, using `bisect`. So 69 is a `"D"` and 70 is a `"C"`.
