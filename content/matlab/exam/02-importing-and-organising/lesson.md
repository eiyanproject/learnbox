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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **table** | named columns of any type, all the same height |
| **import** | read a file into a table |
| **convert** | turn text columns into `datetime` or `categorical` |
| **`NaN`** | how a blank in a numeric column arrives |
| **drop rows** | remove rows with any missing value |
| **busiest** | the value with the most rows |
| **tie** | two values equally common; here the first wins |
| **inclusive window** | dates from `lo` to `hi`, both ends included |
| **unused category** | a category no row uses, still kept by grouping |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `readtable(filename)` | reads a CSV |
| `datetime(t.Day)`, `categorical(t.Station)` | converts columns |
| `ismissing(t)`, `rmmissing(t)` | find / drop gaps |
| `t(mask, :)` | the rows where `mask` is true |
| `t{i, 'Var'}` | one value |
| `height(t)` | the number of rows |
| `countcats(c)`, `categories(c)` | counts and names of categories |
| `isbetween(d, lo, hi)` | dates within the window, inclusive |
| `char(x)` | a category as a char array |

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
