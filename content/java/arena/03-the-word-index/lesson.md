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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **index** (of a book) | the list at the back saying which lines or pages each word is on |
| **word** | here, a run of letters; everything else separates words |
| **case-insensitive** | compared in lower case, so `Cat` and `cat` are one word |
| **line number** | counted from 1 |
| **ascending, no repeats** | each list of lines goes up, and a line appears once |
| **frequency** | how many times a word appears, counting every appearance |
| **tie** | two words with the same count; break it alphabetically |
| **top n** | the `n` most frequent words |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac WordIndex.java && java WordIndex` | builds and runs this round's file |

### Java names

| Name | What it does |
|---|---|
| `static Map<String, List<Integer>> build(List<String> lines)` | word to line numbers |
| `static List<String> top(List<String> lines, int n)` | the most frequent words |
| `TreeMap` | a map whose keys come out sorted |
| `line.split("[^A-Za-z]+")` | the runs of letters in a line (empty pieces can appear and must be skipped) |
| `s.toLowerCase()` | lower case |
| `map.computeIfAbsent(k, x -> new ArrayList<>())` | the list for a word, made the first time |
| `map.merge(word, 1, Integer::sum)` | counts a word |
| `Comparator`, `.reversed()`, `.thenComparing(...)` | order by count, then alphabetically |
| `limit(n)` | keep the first `n` of a stream |

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
