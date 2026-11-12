---
title: "Round 1: The count"
summary: Count the votes and name the winner before the clock runs out.
order: 1
files: [count.py]
run: python -i count.py
challenge:
  minutes: 10
  xp: 150
  requires:
    xp: 300
---

The polls have closed and the result is due in ten minutes.

## The task

In `count.py`, write `winner(votes)`.

`votes` is a list of names, one per vote. Return the name with the most
votes.

- If two or more names are level at the top, return the one that comes first
  alphabetically.
- If there are no votes at all, return `None`.
- A vote counts however it was typed: `" ana "`, `"ANA"` and `"Ana"` are all
  votes for the same person. Strip the spaces, and return the name
  capitalised like `"Ana"`: a capital first letter and the rest lower case,
  which is what `str.capitalize()` gives.
- Do not change the list you are given.

```text
winner(["ana", "bo", "ana"])        ->  "Ana"
winner(["bo", "ana"])               ->  "Ana"   (level, so alphabetical)
winner([" BO ", "bo", "Ana"])       ->  "Bo"
winner([])                          ->  None
```

In the third example, `" BO "` and `"bo"` are two votes for Bo and `"Ana"`
is one, so Bo wins outright.

Press **Check** as often as you like. The first time every test passes, you
win the round.
