---
title: "Review 1: values, text and decisions"
summary: Lessons 1 to 6 arriving mixed and unlabelled - numbers, strings, conditionals and loops, with no hint about which is which.
order: 1
files: [review.py]
run: python -i review.py
hints:
  - "`strip()` alone will not do for `normalise_name`: it trims the ends but leaves the double space in the middle. `\" \".join(raw.split())` collapses every run of whitespace, and `title()` then fixes the capitals."
  - "For `fizz_report`, check `n % 15 == 0` first, or you will never reach the FizzBuzz case."
  - "`initials`: split on whitespace, take `word[0]` from each, uppercase it, and join with dots. An empty string has no words, so the result is empty too."
  - "`bmi_category` is a ladder of comparisons on `weight / height ** 2`. Order matters: check the lowest boundary first and let the later branches assume it failed."
---

No new material in this section. Everything here comes from the Beginner
lessons, but the topics are shuffled and the questions do not say which lesson
they are testing — which is the only way to find out whether you know
something or merely recognise it.

## What this covers

Lessons 1 through 6: variables and numbers, strings, functions, conditionals
and loops.

A few things worth re-reading before you start, because they are where mistakes
cluster:

- `str.strip()` removes whitespace from **both** ends and returns a new string;
  it never modifies in place, because strings cannot be modified at all. It
  does nothing to whitespace in the middle — `" ".join(s.split())` is what
  collapses that.
- `title()` uppercases the first letter of every word and **lowercases the
  rest**, so `"MCDONALD"` becomes `"Mcdonald"`. It is not the same as
  `capitalize()`, which only touches the first character of the whole string.
- `split()` with no argument splits on any run of whitespace and discards empty
  pieces; `split(" ")` splits on single spaces and keeps them.
- A chain of `if` / `elif` stops at the first true branch, so the order you
  write the branches in *is* the logic.
- `%` with a positive divisor always gives a non-negative result.

## Your turn

In `review.py`:

- `normalise_name(raw)`: trim surrounding whitespace and capitalise each word,
  so `"  ada  LOVELACE "` becomes `"Ada Lovelace"`
- `fizz_report(n)`: a list of strings for 1 through `n` — `"Fizz"` for
  multiples of 3, `"Buzz"` for 5, `"FizzBuzz"` for both, otherwise the number
  as a string
- `initials(full_name)`: `"ada lovelace king"` becomes `"A.L.K."`, and an empty
  string becomes `""`
- `bmi_category(weight, height)`: `weight / height ** 2`, returning
  `"underweight"` below 18.5, `"normal"` below 25, `"overweight"` below 30, and
  `"obese"` at 30 or above
