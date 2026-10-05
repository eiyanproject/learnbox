---
title: Dictionaries and sets
summary: Look things up by key, count occurrences, and ask set questions like "what do these share?"
order: 8
files: [lookup.py]
run: python -i lookup.py
hints:
  - "`word_counts`: `counts[word] = counts.get(word, 0) + 1`. Lower-case each word and strip punctuation with `.strip(\".,!?;:\")`."
  - "`invert`: build a new dict and, for each `key, value` in `d.items()`, set `result[value] = key`."
  - "`group_by_first_letter`: `groups.setdefault(letter, []).append(word)` creates the list the first time."
  - "`common_friends`: `set(a) & set(b)`, then `sorted(...)` to return a list in order."
---

## Dictionaries

A **dict** maps keys to values. Looking something up by key is fast no
matter how big the dict gets:

```pycon
>>> ages = {"Ana": 31, "Budi": 27}
>>> ages["Ana"]
31
>>> ages["Citra"] = 45   # add or replace
>>> del ages["Budi"]     # remove
>>> ages
{'Ana': 31, 'Citra': 45}
>>> "Ana" in ages        # 'in' checks the keys
True
>>> len(ages)
2
```

A missing key is an error (`KeyError`). `get` returns a default instead:

```pycon
>>> print(ages.get("Dewi"))    # None (the prompt shows nothing for None)
None
>>> ages.get("Dewi", 0)
0
```

## Looping over a dict

```python
for name in ages:                 # keys
    ...
for name, age in ages.items():    # key and value together
    print(f"{name} is {age}")
ages.keys()     ages.values()
```

Dicts remember the order keys were added.

## Counting: the most common dict pattern

```python
counts = {}
for fruit in ["apple", "mango", "apple"]:
    counts[fruit] = counts.get(fruit, 0) + 1
print(counts)
```

```output
{'apple': 2, 'mango': 1}
```

## Grouping

`setdefault` returns the existing value, or inserts the default first:

```python
groups = {}
for word in ["ant", "bee", "asp"]:
    groups.setdefault(word[0], []).append(word)
print(groups)
```

```output
{'a': ['ant', 'asp'], 'b': ['bee']}
```

Keys must be unchangeable values: strings, numbers and tuples work, lists do
not.

## Sets

A **set** holds unique items with no order. Adding a duplicate does nothing:

```pycon
>>> tags = {"python", "web"}
>>> tags.add("python")
>>> len(tags)              # still two items
2
>>> set([3, 1, 3, 2])      # a quick way to drop duplicates
{1, 2, 3}
```

Sets answer membership questions quickly, and do set algebra:

```pycon
>>> a = {"ana", "budi", "citra"}
>>> b = {"budi", "dewi"}
>>> a & b             # in both
{'budi'}
>>> sorted(a | b)     # in either
['ana', 'budi', 'citra', 'dewi']
>>> sorted(a - b)     # in a but not b
['ana', 'citra']
```

A set has no order, so the same set can print its items in a different order
from one run to the next; `sorted()` turns it into a list in a fixed order,
which is why it appears above.

`{}` is an empty **dict**. An empty set is `set()`.

## Your turn

In `lookup.py`, write:

- `word_counts(text)`: a dict of how often each word appears, ignoring case
  and the punctuation `.,!?;:` at the ends of words:
  `word_counts("The cat. The dog!")` gives `{"the": 2, "cat": 1, "dog": 1}`
- `invert(d)`: swap keys and values: `{"a": 1, "b": 2}` gives `{1: "a", 2: "b"}`
- `group_by_first_letter(words)`: a dict whose keys are lower-case first
  letters and whose values are lists of the words starting with that letter,
  in their original order and spelling:
  `group_by_first_letter(["apple", "Avocado", "banana"])` gives
  `{"a": ["apple", "Avocado"], "b": ["banana"]}`
- `common_friends(a, b)`: a **sorted list** of the names that appear in both
  lists: `common_friends(["Zed", "Ana", "Bo"], ["Bo", "Zed", "Cy"])` gives
  `["Bo", "Zed"]`
