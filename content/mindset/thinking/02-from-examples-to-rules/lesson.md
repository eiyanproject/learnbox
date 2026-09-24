---
title: From examples to rules
summary: Turning a vague requirement into concrete cases, finding the edges before writing code, and noticing where the specification is silent.
order: 2
files: [rules.py]
run: python -i rules.py
hints:
  - "`is_valid_username` has four rules; write them as four separate checks rather than one unreadable boolean expression."
  - "The length check is 3 to 16 INCLUSIVE - the test checks both ends, which is exactly where off-by-one lives."
  - "`describe_failure` returns the FIRST rule broken, in the order listed in the lesson - a specific message beats a generic one."
  - "`normalise` lowercases and strips surrounding whitespace, but must not strip internal underscores or change a valid name."
---

Requirements arrive vague. "Usernames should be reasonable" is not something
you can implement, and asking "what exactly do you mean?" usually produces
another vague sentence.

Examples work better than definitions. Write down what should be accepted and
rejected, and the rule falls out.

## Make a table first

| Input | Verdict | Why |
|---|---|---|
| `ada` | accept | |
| `ad` | reject | too short |
| `ada_lovelace_99` | accept | |
| `Ada Lovelace` | reject | space |
| `ada!` | reject | punctuation |
| `""` | reject | empty |
| `  ada  ` | ? | **specification is silent** |

The last row is the valuable one. The question mark means nobody said, and you
are about to decide by accident. Three choices: trim it, reject it, or ask —
and the worst is to not notice you chose.

## Edges are where the bugs are

Once the rule is "3 to 16 characters", the interesting inputs are 2, 3, 16 and
17 — not 8. Every boundary produces two tests, and off-by-one errors live
exactly there. A test at 8 characters passes for both `>= 3` and `> 3`, so it
distinguishes nothing.

## One rule per check

```python
if len(name) < 3 or len(name) > 16 or not name.isascii() or " " in name:
    return False
```

This is correct and useless when it fails: you know something was wrong, not
what. Separate checks let you say *which* rule was broken, which is the
difference between an error message that helps and one that does not.

## Say what is wrong, specifically

"Invalid username" makes the user guess. "Usernames must be at least 3
characters" tells them what to do next. The cost is a few lines; the benefit is
every person who would otherwise have tried four more times and given up.

## Your turn

In `rules.py`, a username is valid when it:

1. is 3 to 16 characters long (inclusive)
2. contains only lowercase letters, digits and underscores
3. starts with a letter
4. does not end with an underscore

Write:

- `normalise(raw)` — strip surrounding whitespace, lowercase
- `is_valid_username(name)` — applied to the raw input after normalising
- `describe_failure(name)` — the first broken rule, as
  `"too short"`, `"too long"`, `"invalid characters"`, `"must start with a letter"`,
  `"must not end with an underscore"`, or `"ok"`
