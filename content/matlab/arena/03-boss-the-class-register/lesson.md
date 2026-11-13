---
title: "Boss: The class register"
summary: A matrix of marks with gaps in it, a list of names, and one struct that has to answer five questions about them.
order: 4
files: [class_report.m]
run: octave --no-gui --quiet --eval "disp(class_report({'ana','bo'}, [80 90; 50 NaN]))"
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 800
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **cell array** | `{'ana', 'bo'}`: holds text of different lengths |
| **character vector** | a char row such as `'ana'` |
| **matrix** | rows and columns; here one row per student, one column per test |
| **column vector** / **row vector** | n-by-1 / 1-by-n |
| **struct** | named fields in one value: `report.best` |
| **field** | one named part of a struct |
| **level** | tied |
| **dimension argument** | `sum(x, 2)` sums along rows, `sum(x, 1)` down columns |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `isnan(x)`, `~isnan(x)` | where scores are / are not missing |
| `x(isnan(x)) = 0` | replaces missing values |
| `sum(x, 2)`, `sum(x, 1)` | row sums / column sums |
| `[m, i] = max(v)` | the largest and its first position |
| `names(mask)` | the names where the mask is true |
| `numel(names)`, `size(scores, 1)` | how many names / rows |
| `struct('averages', a, ...)` or `report.best = ...` | builds the struct |
| `error('class_report:size', ...)` | the error to raise |

---

Reports go home tomorrow. The marks are in a matrix, some tests were missed,
and the summary script does not exist yet.

## The data

- `names` is a cell array of character vectors, one per student, such as
  `{'ana', 'bo', 'cy'}`.
- `scores` is a matrix with **one row per student** and one column per test.
  A test a student missed is `NaN`.

```matlab
names  = {'ana', 'bo', 'cy'};
scores = [ 80  90 100
           50 NaN  60
          NaN NaN NaN ];
```

## The task

Write `report = class_report(names, scores)`, returning a struct with five
fields.

| Field | What it holds |
|---|---|
| `averages` | a **column** vector: each student's mean over the tests they took, or `0` for a student who took none |
| `test_means` | a **row** vector: each test's mean over the students who took it, or `0` for a test nobody took |
| `best` | the name of the student with the highest average; the earliest in `names` if several are level |
| `passed` | a 1-by-n cell array of the names whose average is at least `60`, in their original order |
| `missing` | how many scores are `NaN` |

For the data above:

```text
averages    ->  [90; 55; 0]
test_means  ->  [65 90 80]
best        ->  'ana'
passed      ->  {'ana'}
missing     ->  4
```

If the number of names is not the number of rows of `scores`, raise an error
with the identifier `class_report:size`. There is always at least one
student.

`mean` does not skip `NaN` by itself. Count the valid entries with `~isnan`
and divide the sums by those counts, giving `sum` its dimension argument
(`sum(x, 2)` for rows) so that a class of one student still works.
