---
title: datetime and duration
summary: A point in time and a length of time are different types, and keeping them apart is what stops the units getting lost.
order: 3
files: [parse_dates.m, elapsed_days.m, in_window.m, latest.m]
run: octave --no-gui --quiet --eval "d = parse_dates({'2026-01-01','2026-03-01'}); disp(elapsed_days(d(1), d(2)))"
hints:
  - "`datetime(c)` takes a cell array of date text and gives a datetime array."
  - "Wrap it in try/catch and rethrow with your own identifier, so a bad row is reported as a parse problem rather than leaking the internal message."
  - "`d2 - d1` is a duration, not a number. `days(...)` turns it into one."
  - "`isbetween(dates, lo, hi)` gives a logical mask, and it is inclusive at both ends."
---

```matlab
d = datetime(2026, 1, 2);
d = datetime('2026-01-02');
```

A datetime is a **point in time**. Subtract two of them and you do not get a
number — you get a **duration**, which is a *length* of time:

```matlab
gap = datetime(2026, 3, 1) - datetime(2026, 1, 1);   % a duration
days(gap)                                            % 59
```

That is the entire argument for these types. A bare number of days does not
know it is days: multiply it by 24 and nothing complains, and six months later
nobody can tell whether the column was hours or days. A duration knows, and
converting is explicit.

```matlab
days(gap)   hours(gap)   minutes(gap)   seconds(gap)
```

The same names build durations from numbers — `days(7)` is a duration of a
week — so they read the same in both directions.

## Arithmetic that makes sense

| | |
|---|---|
| datetime − datetime | duration |
| datetime + duration | datetime |
| duration + duration | duration |
| duration × number | duration |
| datetime + number | **an error** |

That last row is the point. Adding a plain `7` to a date is ambiguous — seven
of what? — so it is refused, and you write `d + days(7)`.

## Components and comparison

```matlab
year(d)   month(d)   day(d)   hour(d)   minute(d)   second(d)

d1 < d2                          % chronological
isbetween(d, lo, hi)             % inclusive at both ends
sort(dates)   max(dates)   min(dates)
```

Comparison is on the instant, not on how the text was written, so
`'2026-01-02'` and `'02-Jan-2026'` compare equal once parsed.

## Parsing

`datetime('2026-01-02')` reads ISO order without being told. Anything
ambiguous — `'01/02/2026'` — is a guess, and a guess about day-month order is
one you will regret. Prefer ISO, and where the input is fixed, say the format
explicitly.

## Your turn

- `parse_dates(c)` — a datetime array from a cell array of text, throwing
  `parse_dates:bad` when an entry will not parse
- `elapsed_days(d1, d2)` — the number of days from `d1` to `d2`
- `in_window(dates, lo, hi)` — a logical mask, inclusive
- `latest(dates)` — the latest datetime, throwing `latest:empty` for none
