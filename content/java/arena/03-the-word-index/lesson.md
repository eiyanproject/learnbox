---
title: "Round 3: The word index"
summary: Build the index at the back of a book - which lines each word is on - and rank the words by how often they appear.
order: 3
files: [WordIndex.java]
run: javac WordIndex.java && java WordIndex
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 1000
---

The manual goes to print tonight and it has no index.

## The task

In `WordIndex.java`, write two static methods.

A **word** is a run of letters. Everything else - spaces, digits,
punctuation - separates words, so `"don't"` is the two words `don` and `t`.
Words are compared in lower case, and lines are numbered from 1.

### `Map<String, List<Integer>> build(List<String> lines)`

Map each word to the numbers of the lines it appears on.

- the keys are lower-case and come out in alphabetical order when the map is
  iterated (a `TreeMap` does that)
- each list is in ascending order with no repeats: a word that appears twice
  on line 3 lists line 3 once

```text
lines:  1  "The cat sat."
        2  "The Cat? The mat!"

build   ->  {cat=[1, 2], mat=[2], sat=[1], the=[1, 2]}
```

### `List<String> top(List<String> lines, int n)`

The `n` most frequent words, counting **every** appearance, most frequent
first. Words that appear equally often go in alphabetical order. If there
are fewer than `n` different words, return them all. `n` of zero or less
gives an empty list.

```text
top(lines, 2)   ->  [the, cat]       (the appears 3 times, cat twice)
```
