---
title: Importing and cleaning
summary: Read a file into a table, find what is missing, decide what to do about it, and summarise by group.
order: 5
files: [load_clean.m, missing_count.m, average_by.m]
run: octave --no-gui --quiet --eval "t = readtable('readings.csv'); disp(missing_count(t))"
hints:
  - "`readtable(filename)` returns a table, with a numeric column wherever every entry parsed as a number."
  - "A blank in a numeric column becomes NaN, which is what `ismissing` finds."
  - "`ismissing(t)` gives a logical matrix, one entry per cell. `sum(sum(...))` counts them all."
  - "`groupsummary(t, group, 'mean', data)` gives one row per group, with a GroupCount and a mean_<data> variable."
---

Real data arrives in a file and arrives imperfect. This is the shape of nearly
every MATLAB job.

## Reading

```matlab
t = readtable('readings.csv');
```

A column becomes **numeric** when every entry parses as a number, and text
otherwise. A blank in an otherwise-numeric column becomes `NaN` — which is
exactly what you want, because `NaN` is a value the missing-data functions can
find, whereas an empty string in a numeric column would not be.

A date column arrives as **text**. Converting it is a deliberate step:

```matlab
t.Day = datetime(t.Day);
```

## Finding what is missing

```matlab
ismissing(t)        % a logical matrix, one entry per cell
```

What counts as missing depends on the type: `NaN` for numbers, `''` for text,
`<undefined>` for a categorical. `ismissing` knows the difference, which a hand
written `isnan` check would not.

## Deciding what to do

```matlab
rmmissing(t)        % drop every row with any missing value
```

Dropping is one answer and not always the right one. Six rows with one gap each
can lose most of a small table. The alternatives are to fill (`fillmissing`),
to drop only rows missing the variable you actually need, or to keep the gap
and let the statistics ignore it — `mean(v, 'omitnan')` does.

The wrong answer is to replace missing values with zero without saying so. A
zero temperature is a temperature.

## Summarising by group

```matlab
groupsummary(t, 'Station', 'mean', 'Reading')
```

One row per group, with a `GroupCount` and a `mean_Reading`. This is the
grouped-aggregate step you would write as `GROUP BY` in SQL, and doing it with
a loop over unique values is the thing it replaces.

Convert the grouping column to a categorical first when the set of values
matters — then a group with no rows still appears, with a count of zero.

## Your turn

`readings.csv` has `Station`, `Day`, `Reading` and `Quality`, and one gap.

- `load_clean(filename)` — read it and drop rows with anything missing
- `missing_count(t)` — how many missing values a table holds
- `average_by(t, groupVar, dataVar)` — the grouped means
