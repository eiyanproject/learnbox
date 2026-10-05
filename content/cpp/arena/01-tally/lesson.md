---
title: "Round 1: Tally"
summary: Two short functions over vectors. The standard library does most of the work if you let it.
order: 1
files: [tally.cpp, tally.h]
run: g++ -std=c++20 -Wall -c tally.cpp
challenge:
  minutes: 12
  xp: 150
  requires:
    xp: 100
---

Two warm-up functions. The header is written; define them in `tally.cpp`.

## The task

`std::string most_common(const std::vector<std::string>& words)` returns the
word that appears most often.

- If several words are level, return the one that comes first
  alphabetically.
- An empty vector gives an empty string.
- Words are compared exactly as they are: `"Tea"` and `"tea"` are different.

```text
most_common({"tea", "coffee", "tea"})    ->  "tea"
most_common({"tea", "coffee"})           ->  "coffee"   (level, so alphabetical)
most_common({})                          ->  ""
```

`std::vector<int> unique_sorted(const std::vector<int>& values)` returns the
distinct values in ascending order.

```text
unique_sorted({3, 1, 3, 2, 1})   ->  {1, 2, 3}
unique_sorted({})                ->  {}
```
