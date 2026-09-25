---
title: "Paper 2: importing and organising"
summary: A file becomes a table, the columns become types that mean something, and the gaps get dealt with.
order: 2
files: [load_typed.m, busiest_station.m, window_rows.m]
run: octave --no-gui --quiet --eval "t = load_typed('sensors.csv'); disp(height(t))"
hints:
  - "Convert before cleaning, so a converted column's gaps are visible to ismissing."
  - "`groupsummary(t, var)` with no method gives one row per group and a GroupCount."
  - "`isbetween(dates, lo, hi)` is inclusive at both ends, and gives a mask you can use as a row subscript."
---

The second paper covers the **Intermediate** ground: cell arrays and structs,
tables, `datetime`, `categorical`, and the import-and-clean sequence. This is
the largest scored domain on the Associate exam.

`sensors.csv` holds `Station`, `Day`, `Reading` and `Quality`, eight rows, and
one gap in `Reading`.

Worth having straight:

- a numeric column with a blank arrives as `NaN`, which `ismissing` finds
- a date column arrives as **text** until you convert it
- `t(mask, :)` selects rows; `t{i, 'Var'}` reaches one value
- grouping a categorical keeps categories that no row uses

## Your turn

- `load_typed(filename)` — read the file, convert `Day` to `datetime` and
  `Station` to `categorical`, then drop any row with a missing value
- `busiest_station(t)` — the `Station` with the most rows, as a char array;
  ties go to whichever comes first. Throws `busiest_station:empty` for an
  empty table.
- `window_rows(t, lo, hi)` — the rows whose `Day` falls within `[lo, hi]`,
  inclusive, as a table
