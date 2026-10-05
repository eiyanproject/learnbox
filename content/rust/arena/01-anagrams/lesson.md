---
title: "Round 1: Anagrams"
summary: Decide whether two phrases use the same letters, then sort a word list into its anagram families.
order: 1
files: [src/lib.rs]
run: cargo test
challenge:
  minutes: 12
  xp: 150
  requires:
    xp: 300
---

A crossword setter needs their word list sorted into anagram families
before the print deadline.

## The task

In `src/lib.rs`, write two functions.

`pub fn are_anagrams(a: &str, b: &str) -> bool` is `true` when the two
texts are made of exactly the same letters, the same number of times each.
Case does not matter, and anything that is not a letter - spaces,
punctuation, digits - is ignored.

```text
are_anagrams("listen", "silent")            ->  true
are_anagrams("Dormitory", "dirty room")     ->  true
are_anagrams("aab", "abb")                  ->  false
```

`pub fn group_anagrams(words: &[&str]) -> Vec<Vec<String>>` sorts the words
into groups of mutual anagrams.

- A group appears where its first word appeared in the input.
- Inside a group the words keep their input order and their spelling.
- A word with no anagram is a group of one.

```text
group_anagrams(&["eat", "tea", "tan", "ate", "nat", "bat"])
->  [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
```
