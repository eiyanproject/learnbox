---
title: "Round 2: Squeeze"
summary: Shrink a string by counting its runs, then bring it back.
order: 2
files: [squeeze.py]
run: python -i squeeze.py
challenge:
  minutes: 15
  xp: 200
  requires:
    xp: 600
---

The link is slow and the message is repetitive. Pack it down, send it, and
unpack it at the other end.

## The task

In `squeeze.py`, write two functions.

`squeeze(text)` replaces every run of the same character with the character
followed by the length of the run. A character that appears on its own keeps
no number.

```text
squeeze("aaabccdddd")   ->  "a3bc2d4"
squeeze("abc")          ->  "abc"
squeeze("")             ->  ""
```

`unsqueeze(packed)` does the reverse.

```text
unsqueeze("a3bc2d4")    ->  "aaabccdddd"
unsqueeze("x12")        ->  "xxxxxxxxxxxx"
```

The text is only ever letters, never digits, so a digit in the packed form is
always part of a count. A count can have more than one digit. For any text,
`unsqueeze(squeeze(text))` gives the text back.
