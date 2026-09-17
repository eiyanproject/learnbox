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

```python
ages = {"Ana": 31, "Budi": 27}
ages["Ana"]          # 31
ages["Citra"] = 45   # add or replace
del ages["Budi"]     # remove
"Ana" in ages        # True: 'in' checks keys
len(ages)            # 2
```

A missing key is an error (`KeyError`). `get` returns a default instead:

```python
ages.get("Dewi")        # None
ages.get("Dewi", 0)     # 0
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
# {'apple': 2, 'mango': 1}
```

## Grouping

`setdefault` returns the existing value, or inserts the default first:

```python
groups = {}
for word in ["ant", "bee", "asp"]:
    groups.setdefault(word[0], []).append(word)
# {'a': ['ant', 'asp'], 'b': ['bee']}
```

Keys must be unchangeable values: strings, numbers and tuples work, lists do
not.

## Sets

A **set** holds unique items with no order. Adding a duplicate does nothing:

```python
tags = {"python", "web"}
tags.add("python")      # still two items
set([3, 1, 3, 2])       # {1, 2, 3}: a quick way to drop duplicates
```

Sets answer membership questions quickly, and do set algebra:

```python
a = {"ana", "budi", "citra"}
b = {"budi", "dewi"}
a & b     # {'budi'}                 in both
a | b     # all four names           in either
a - b     # {'ana', 'citra'}         in a but not b
```

`{}` is an empty **dict**. An empty set is `set()`.

## Your turn

In `lookup.py`, write:

- `word_counts(text)`: a dict of how often each word appears, ignoring case
  and the punctuation `.,!?;:` at the ends of words
- `invert(d)`: swap keys and values: `{"a": 1, "b": 2}` gives `{1: "a", 2: "b"}`
- `group_by_first_letter(words)`: a dict from lower-case first letter to the
  list of words starting with it, in their original order
- `common_friends(a, b)`: a **sorted list** of names that appear in both lists
