---
title: "Round 3: Durations"
summary: Parse "1h30m" into seconds and back, with an error type that says exactly what was wrong with the text.
order: 3
files: [src/lib.rs]
run: cargo test
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 1300
---

The scheduler's config file says `timeout = 1h30m`. Something has to read
that, and something has to print it back in the logs.

## The task

In `src/lib.rs`, write two functions. The error type is already in the
file; do not change it.

### `pub fn parse_duration(text: &str) -> Result<u64, ParseError>`

The text is one or more parts, each a whole number followed by a unit, with
nothing between them. Return the total in seconds.

| Unit | Seconds |
|---|---|
| `d` | 86400 |
| `h` | 3600 |
| `m` | 60 |
| `s` | 1 |

```text
parse_duration("90s")       ->  Ok(90)
parse_duration("1h30m")     ->  Ok(5400)
parse_duration("2d5s")      ->  Ok(172805)
parse_duration("30m1h")     ->  Ok(5400)     (any order is fine)
```

What is wrong, checked as you read from left to right, and the error for
each:

- the text is empty: `Empty`
- a unit letter with no number in front of it, as in `"h"` or `"5mm"`:
  `MissingNumber`
- a character that is neither a digit nor one of the four units, as in
  `"5x"`: `UnknownUnit` holding that character
- a unit used a second time, as in `"1h2h"`: `Repeated` holding the unit
- the text ends in a number with no unit, as in `"5"` or `"1h30"`:
  `MissingUnit`

Stop at the first problem.

### `pub fn format_duration(seconds: u64) -> String`

The reverse, using the largest units first and leaving out any that are
zero. Zero seconds is `"0s"`.

```text
format_duration(5400)     ->  "1h30m"
format_duration(172805)   ->  "2d5s"
format_duration(0)        ->  "0s"
```

For any `n`, `parse_duration(&format_duration(n))` is `Ok(n)`.
