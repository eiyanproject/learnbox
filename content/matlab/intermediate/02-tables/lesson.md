---
title: Tables
summary: Columns of different types with names, all the same height - and t(1,'Age') against t{1,'Age'}, which the exam asks about directly.
order: 2
files: [adults_only.m, add_bmi.m, tallest_name.m]
run: octave --no-gui --quiet --eval "t = table({'a';'b'},[36;17],[1.7;1.6],[70;55],'VariableNames',{'Name','Age','Height','Weight'}); disp(adults_only(t))"
hints:
  - "`t.Age` gives one variable as its own array. `t(rows, :)` gives a smaller TABLE."
  - "Logical row selection reads exactly as it sounds: `t(t.Age >= 18, :)`."
  - "Add a variable by assigning to a new name: `t.BMI = t.Weight ./ t.Height .^ 2;` - element-wise, so the dots matter."
  - "`t{i, 'Name'}` reaches the value inside. For a text column that is a char array, not a 1x1 table."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **table** | columns of different types, each named, all the same height |
| **variable** (of a table) | one named column |
| **height** / **width** | rows / variables |
| **parentheses keep the container** | `t(1, 'Age')` is a 1x1 table |
| **braces reach through** | `t{1, 'Age'}` is the value |
| **logical subscript** | a true/false column that selects rows |
| **BMI** | body mass index: weight over height squared |
| **element-wise power** | `.^`: squares each element |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `table(a, b, 'VariableNames', {'Age', 'Name'})` | builds a table |
| `height(t)`, `width(t)` | rows, variables |
| `t.Age` | one variable as a plain array |
| `t(1:3, :)`, `t(:, {'Age'})` | smaller tables |
| `t{1, 'Age'}` | one value |
| `t(t.Age >= 18, :)` | filters rows |
| `t.BMI = t.Weight ./ t.Height .^ 2;` | adds a variable |
| `addvars`, `removevars`, `renamevars` | the same jobs by name |
| `sortrows(t, 'Age', 'descend')` | sorts whole rows |
| `t.Properties.VariableNames` | the variable names |
| `[~, i] = max(t.Height)` | the position of the largest, ignoring the value |

---

A table holds columns of different types side by side, each with a name, all
the same height. That is what separates it from a matrix, which is one type
with no names, and from a struct of arrays, where nothing keeps the lengths in
step.

```matlab
t = table(ages, names, 'VariableNames', {'Age', 'Name'});
height(t)      % rows
width(t)       % variables
```

Note `height`, not `numel` or `length`. A table's size is `[rows, variables]`,
and `height` says which one you meant.

## Getting at the data

```matlab
t.Age              % the variable itself - a plain array
t(1:3, :)          % a smaller TABLE, first three rows
t(:, {'Age'})      % a TABLE of one variable
t{1, 'Age'}        % the NUMBER in that cell
```

**Parentheses keep the container; braces reach through it.** `t(1,'Age')` is a
1×1 table and `t{1,'Age'}` is the value inside. This is the same distinction as
cell arrays, and it is asked about directly.

## Selecting rows

```matlab
t(t.Age >= 18, :)
```

`t.Age >= 18` is a logical column, and a logical subscript selects rows. This
is the whole of filtering — no loop, and it reads as the sentence it is.

## Adding a variable

```matlab
t.BMI = t.Weight ./ t.Height .^ 2;
```

Assigning to a name that does not exist adds it; to one that does, replaces it.
The height must match. `t.BMI = []` removes it.

`addvars`, `removevars` and `renamevars` do the same jobs when the name is in a
variable rather than typed out.

## Sorting

```matlab
sortrows(t, 'Age')
sortrows(t, 'Age', 'descend')
```

Whole rows move together, which is the point: sorting one column of a matrix
and not the others silently destroys the data.

## Properties

```matlab
t.Properties.VariableNames
```

The names live here rather than in a variable of their own.

## Run

```matlab
t = table([12; 30; 45], {'ann'; 'bo'; 'cy'}, 'VariableNames', {'Age', 'Name'});
fprintf('%d rows, %d variables\n', height(t), width(t));
disp(class(t(1, 'Age')))
disp(t{1, 'Age'})
adults = t(t.Age >= 18, :);
disp(height(adults))
oldest = sortrows(t, 'Age', 'descend');
disp(oldest.Age')
names = oldest.Name;
fprintf('%s ', names{:}); fprintf('\n');
```

```output
3 rows, 2 variables
table
12
2
45 30 12
cy bo ann
```

## Your turn

The table has `Name`, `Age`, `Height` (metres) and `Weight` (kg).

- `adults_only(t)` — the rows where `Age` is 18 or more
- `add_bmi(t)` — the same table with a `BMI` variable, weight over height squared
- `tallest_name(t)` — the `Name` of the tallest row, as a char array
