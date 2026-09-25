---
title: A readings report
summary: The capstone - read a file, convert the columns to the types that mean something, clean it, group it, and say what it found.
order: 4
files: [load_readings.m, daily_summary.m, report_line.m]
run: octave --no-gui --quiet --eval "t = load_readings('sensors.csv'); disp(report_line(t))"
hints:
  - "`load_readings` does four things in order: read, convert Day to datetime, convert Station to categorical, drop missing rows."
  - "Convert before cleaning, so a gap in a converted column is visible to ismissing."
  - "`daily_summary` is one call to groupsummary, grouping by Station and taking the mean of Reading."
  - "`report_line` needs the station with the highest mean: `[~, at] = max(g.mean_Reading)` and then index the group column."
---

Everything in the track, on one file.

```
sensors.csv  ->  table  ->  typed  ->  cleaned  ->  grouped  ->  a sentence
```

## Read

`readtable` gives a table where numeric columns are numeric and everything else
is text. That is the most it can know from a text file.

## Convert

```matlab
t.Day = datetime(t.Day);
t.Station = categorical(t.Station);
```

This is the step that turns data into *typed* data, and it is deliberate. A
date as text sorts alphabetically, which is right for ISO order and wrong for
every other format. A station as text can be grouped, but nothing stops
`'north'` and `'North '` being two stations.

**Convert before cleaning.** A gap that became `NaN` on import is visible to
`ismissing`; the same gap left as `''` in a text column is visible too, but a
column half converted is not.

## Clean

```matlab
rmmissing(t)
```

Decide, and say what you decided. Dropping rows is defensible when the gaps are
few and scattered; it is not when one column is half empty, because you will
throw away every row for the sake of one variable.

## Group

```matlab
groupsummary(t, 'Station', 'mean', 'Reading')
```

One row per station, a `GroupCount`, and a `mean_Reading`. The count is what
tells you whether the mean is worth anything: a mean of one reading is that
reading.

## Report

```matlab
sprintf('%d readings from %d stations; highest mean %s at %.1f', ...)
```

The last step of most real jobs is a sentence a person can read. Formatting is
not decoration: `%.1f` on a temperature says how much precision you are
claiming.

## Your turn

`sensors.csv` has `Station`, `Day`, `Reading` and `Quality`, and one gap.

- `load_readings(filename)` — read, convert, clean
- `daily_summary(t)` — the per-station table from `groupsummary`
- `report_line(t)` — a single char row:
  `'<n> readings from <k> stations; highest mean <station> at <x.x>'`
