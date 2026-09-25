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

## Your turn

The table has `Name`, `Age`, `Height` (metres) and `Weight` (kg).

- `adults_only(t)` — the rows where `Age` is 18 or more
- `add_bmi(t)` — the same table with a `BMI` variable, weight over height squared
- `tallest_name(t)` — the `Name` of the tallest row, as a char array
