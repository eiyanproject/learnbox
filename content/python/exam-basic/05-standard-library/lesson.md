---
title: "Paper 5: a standard library tour"
summary: statistics, datetime, re and json - the batteries the exam expects you to know are included.
order: 5
files: [toolbox.py]
run: python -i toolbox.py
hints:
  - "`statistics` has `mean`, `median` and two standard deviations: `pstdev` for a whole population, `stdev` for a sample. The exam means the population one here."
  - "`datetime.date.fromisoformat(\"2026-09-23\")` parses an ISO date. `weekday()` is Monday=0 through Sunday=6, and `timetuple().tm_yday` is the day of the year."
  - "`re.findall(pattern, text)` returns every match as a list. A group in the pattern changes what is returned, so use a non-capturing group or no group at all."
  - "`json.dumps(obj, sort_keys=True)` makes the output deterministic; `json.loads` reads it back. A tuple becomes a list on the round trip - JSON has no tuples."
---

The syllabus calls this "a brief tour of the standard library" and gives it four
questions. The point is not to memorise every module, but to know which one
already solves the problem.

## statistics

```pycon
>>> import statistics
>>> statistics.mean([1, 2, 3, 4])
2.5
>>> statistics.median([1, 2, 3, 4])            # the average of the middle two
2.5
>>> round(statistics.pstdev([1, 2, 3, 4]), 3)  # population
1.118
>>> round(statistics.stdev([1, 2, 3, 4]), 3)   # sample, divides by n-1
1.291
```

The **mean** is the ordinary average: the sum divided by the count. The
**median** is the middle value once the numbers are sorted; with an even
count there are two middle values, and the median is their average. The
**standard deviation** measures how spread out the values are around the
mean.

Two standard deviations exist and they give different answers. `pstdev` treats
the data as the entire population, and divides by `n`; `stdev` treats it as a
sample taken from a larger population, and divides by `n - 1`, which gives a
slightly larger number. With a single value, `pstdev` is `0.0`, but `stdev`
raises an error, since a sample of one says nothing about spread.

## datetime

```pycon
>>> from datetime import date
>>> d = date.fromisoformat("2026-09-23")      # a Wednesday
>>> d.weekday()                # Monday is 0, Sunday is 6
2
>>> d.isoweekday()             # Monday is 1 - a different convention
3
>>> d.strftime("%Y/%m/%d")
'2026/09/23'
>>> d.timetuple().tm_yday      # day of the year
266
```

`weekday()` and `isoweekday()` differ by one. That is a question waiting to
happen.

`fromisoformat` reads a date written in the ISO form, year-month-day.
`strftime` ("string format time") writes it back out using codes: `%Y` is the
four-digit year, `%m` the month and `%d` the day, each with a leading zero.
`timetuple().tm_yday` counts days from 1 January, which is day 1, so it
includes 29 February in a leap year: 1 March is day 61 in 2024 but day 60 in
2026.

```pycon
>>> date.fromisoformat("2024-03-01").timetuple().tm_yday
61
>>> date.fromisoformat("2026-03-01").timetuple().tm_yday
60
```

## re

```pycon
>>> import re
>>> re.findall(r"\d+", "a1 b22")       # every match
['1', '22']
>>> re.search(r"\d+", "a1 b22")        # a match object for the first, or None
<re.Match object; span=(1, 2), match='1'>
>>> print(re.match(r"\d+", "a1"))      # match only anchors at the start
None
```

`findall` returns strings; `search` and `match` return match objects you call
`.group()` on. `match` anchors at the beginning, `search` scans — another
reliable exam distinction.

`\d+` means "one or more digits", and `[A-Z]` means "one capital letter".
Braces give an exact count: `[A-Z]{2}` is exactly two capitals. With round
brackets (a **group**) in the pattern, `findall` returns only the bracketed
part of each match, not the whole match, which is a common surprise:

```pycon
>>> re.search(r"\d+", "a1 b22").group()
'1'
>>> re.findall(r"[a-z](\d+)", "a1 b22")        # a group: only the digits
['1', '22']
>>> re.findall(r"[a-z]\d+", "a1 b22")          # no group: the whole match
['a1', 'b22']
```

## json

```pycon
>>> import json
>>> json.dumps({"b": 1, "a": 2}, sort_keys=True)
'{"a": 2, "b": 1}'
>>> json.loads('{"a": 1}')
{'a': 1}
```

`dumps` (dump to a string) turns Python data into JSON text, and `loads`
(load from a string) does the reverse. `sort_keys=True` writes the keys in
alphabetical order, so the same data always gives the same text.

JSON has no tuples and no sets: a tuple serialises to an array and comes back
as a **list**, and a set cannot be serialised at all. Dict keys always come
back as strings, because JSON object keys must be strings:

```pycon
>>> json.loads(json.dumps({"point": (1, 2)}))
{'point': [1, 2]}
>>> json.loads(json.dumps({1: "one"}))
{'1': 'one'}
```

## Your turn

In `toolbox.py`:

- `summarise(values)`: a dict with the `mean`, the `median` and the `stdev`
  of the numbers, using the `statistics` module. The standard deviation is
  the **population** one (`pstdev`), rounded to 3 decimals.
  `summarise([2, 4, 4, 4, 5, 5, 7, 9])` is
  `{"mean": 5, "median": 4.5, "stdev": 2.0}`, and a single value such as
  `[5]` gives a `stdev` of `0.0`. (`statistics.mean` of whole numbers that
  average out exactly returns an `int`, which is why the mean shows as `5`.)
- `date_facts(iso)`: `iso` is a date written like `"2026-03-07"`. Return a
  dict with `formatted` (the date as `YYYY/MM/DD`), `weekday` (a number,
  Monday is 0), `day_of_year` (1 January is 1) and `is_weekend` (true on
  Saturday and Sunday). For `"2026-03-07"`, a Saturday, that is
  `{"formatted": "2026/03/07", "weekday": 5, "day_of_year": 66, "is_weekend": True}`.
- `find_codes(text)`: a list of every code in the text, in order, where a
  code is two upper-case letters followed by three digits.
  `"ship AB123 and xy999, then ZZ007."` gives `["AB123", "ZZ007"]`;
  lower-case letters or only two digits (`"AB12"`) do not count.
- `round_trip(obj)`: turn the object into JSON text with its keys sorted,
  then read that text back into an object. Return both as a tuple,
  `(json_text, restored_object)`: `round_trip({"b": 1, "a": [1, 2]})` is
  `('{"a": [1, 2], "b": 1}', {"a": [1, 2], "b": 1})`.
