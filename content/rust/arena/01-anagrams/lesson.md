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

## Details the tests check

- Letters are compared without regard to case, so the groups are too:
  `"Tea"` and `"EAT"` belong together, and each keeps its own spelling in
  the output.
- Digits count as "not a letter": `are_anagrams("r2d2", "dr")` is `true`.
- Two texts with no letters at all are anagrams of each other:
  `("", "")` and `("", " !? ")` are both `true`, but `("", "a")` is not.
- A word that appears twice is kept twice: `["on", "no", "on"]` is one
  group of three.
- No words give no groups (an empty `Vec`).

A useful idea: two words are anagrams exactly when their letters, lower-cased
and sorted, are the same. That sorted form makes a good `HashMap` key; keep
the groups in a `Vec` so their order follows the input.
