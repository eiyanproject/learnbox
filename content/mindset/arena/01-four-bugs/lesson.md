---
title: "Round 1: Four bugs"
summary: Four short functions, one bug in each. Find the one wrong thing; do not rewrite.
order: 1
files: [report.py]
run: python -i report.py
challenge:
  minutes: 10
  xp: 150
  requires:
    xp: 50
---

`report.py` went out on Friday. Four bug reports came in over the weekend,
one for each function.

## The task

Each function in `report.py` has a docstring saying what it should do, and
**exactly one bug**. Fix all four.

The reports, as the users wrote them:

1. "`average([])` crashes instead of giving 0."
2. "`longest_word('one two six')` says `six`. It should say `one`: when
   several words are the longest, I want the first."
3. "`running_total([1, 2, 3])` gives `[2, 5]`. I expected `[1, 3, 6]`."
4. "`percent(1, 4)` gives `0.0`. A quarter is 25%."

Each fix is a small change to one line, or one line added. If you are
rewriting a whole function, read its report again.
