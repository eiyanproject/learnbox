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

A **dict** (short for dictionary) stores pairs: each **key** is linked to a
**value**. Think of a real dictionary, where you look up a word (the key) to
find its meaning (the value), or a phone book, where a name leads to a number.
A list finds things by position; a dict finds them by key, so you never need
to know *where* something is stored, only what it is called.

A dict is written with curly braces, with a colon between each key and its
value and commas between the pairs. Looking something up by key is fast no
matter how big the dict gets, because Python does not search through the
pairs one by one; it jumps straight to the right place.

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

Each key appears at most once. Assigning to a key that already exists
replaces its value; assigning to a new key adds a pair. The same line,
`ages["Citra"] = 45`, does whichever is needed.

Asking for a key that is not there is an error, a `KeyError`. When a key
might be missing, use `get` instead: it returns the value if the key exists,
and otherwise a default, which is `None` unless you give your own:

```pycon
>>> ages["Dewi"]
Traceback (most recent call last):
  ...
KeyError: 'Dewi'
>>> print(ages.get("Dewi"))
None
>>> ages.get("Dewi", 0)
0
```

(`print()` is used for the first `get` because the prompt shows nothing at
all when a result is `None`.)

## Looping over a dict

Looping over a dict directly gives you its keys. `.items()` gives you each
key and value together as a pair, which you unpack into two names.
`.values()` gives only the values:

```python
ages = {"Ana": 31, "Citra": 45}

for name in ages:                 # the keys only
    print(name)

for name, age in ages.items():    # key and value together
    print(f"{name} is {age}")

for age in ages.values():         # the values only
    print(age)
```

```output
Ana
Citra
Ana is 31
Citra is 45
31
45
```

Dicts remember the order keys were added, so a loop always visits them in
that order.

## Counting: the most common dict pattern

To count how many times each thing appears, use the things as keys and the
counts as values. The trick is `counts.get(fruit, 0)`: the current count, or
0 if this is the first time the fruit has turned up. Adding 1 and storing it
back works for the first time and every time after:

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

Grouping means collecting items into lists, one list per key: all the words
starting with "a" in one list, all those starting with "b" in another.
`setdefault(key, default)` does the awkward part. If the key is already in
the dict, it returns the value stored there. If not, it first stores the
default under that key and then returns it. Either way you get back the list
for that key, ready to `append` to:

```python
groups = {}
for word in ["ant", "bee", "asp"]:
    groups.setdefault(word[0], []).append(word)
print(groups)
```

```output
{'a': ['ant', 'asp'], 'b': ['bee']}
```

Going through it: for `"ant"`, there is no `"a"` key yet, so an empty list
is stored under `"a"` and `"ant"` is appended to it. For `"bee"`, the same
happens with `"b"`. For `"asp"`, the `"a"` list already exists, so
`setdefault` returns it and `"asp"` joins `"ant"`.

Keys must be values that cannot change: strings, numbers and tuples work,
lists do not. The reason is that the dict files each pair according to its
key, so if a key could change after it was stored, the dict could no longer
find it. Using a list as a key is a `TypeError`. Values have no such rule;
anything can be a value, including lists and other dicts.

## Sets

A **set** holds unique items with no order: each value is either in the set
or not, and it cannot be in it twice. It is written with curly braces like a
dict, but with single values instead of `key: value` pairs. Adding a
duplicate does nothing:

```pycon
>>> tags = {"python", "web"}
>>> tags.add("python")
>>> len(tags)              # still two items
2
>>> set([3, 1, 3, 2])      # a quick way to drop duplicates
{1, 2, 3}
```

Sets answer "is this in here?" (`x in tags`) as quickly as a dict looks up a
key, no matter how large they get; `in` on a list has to check the items one
by one. Sets also do set algebra, the operations from maths lessons with
Venn diagrams: `&` gives the items in both sets (the intersection), `|` the
items in either set (the union), and `-` the items in the first but not the
second (the difference):

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

Because a set has no order, it has no positions either: `tags[0]` is an
error. To go through a set, loop over it with `for`, or sort it first.

`{}` is an empty **dict**, not an empty set; dicts came first, so they got the
short form. An empty set is written `set()`.

## Your turn

In `lookup.py`, write:

- `word_counts(text)`: a dict of how often each word appears, ignoring case
  and the punctuation `.,!?;:` at the ends of words:
  `word_counts("The cat. The dog!")` gives `{"the": 2, "cat": 1, "dog": 1}`.
  "Ignoring case" means `The` and `the` count as the same word, so lower-case
  each word before counting it. `.strip(".,!?;:")` removes any of those
  characters from both ends of a word, but leaves the middle alone.
- `invert(d)`: a new dict with the keys and values swapped, so each old value
  becomes a key and points back at its old key: `{"a": 1, "b": 2}` gives
  `{1: "a", 2: "b"}`. You can assume no two keys share a value.
- `group_by_first_letter(words)`: a dict whose keys are lower-case first
  letters and whose values are lists of the words starting with that letter,
  in their original order and spelling:
  `group_by_first_letter(["apple", "Avocado", "banana"])` gives
  `{"a": ["apple", "Avocado"], "b": ["banana"]}`
- `common_friends(a, b)`: a **sorted list** of the names that appear in both
  lists: `common_friends(["Zed", "Ana", "Bo"], ["Bo", "Zed", "Cy"])` gives
  `["Bo", "Zed"]`
