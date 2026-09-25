---
title: Cell arrays and structs
summary: Two ways to hold things that are not all the same - and the braces that reach inside a cell, which is the distinction everything else follows from.
order: 1
files: [count_type.m, longest.m, make_record.m, field_or.m]
run: octave --no-gui --quiet --eval "disp(longest({'a', 'abc', 'ab'}))"
hints:
  - "`c(2)` gives a 1x1 CELL. `c{2}` gives what is inside it. Nearly every cell array bug is one of those where the other was meant."
  - "`cellfun(@(x) strcmp(class(x), name), c)` gives a logical array; sum it."
  - "A struct is built by assigning fields: `r.name = name; r.age = age;` - or in one call with `struct('name', name, 'age', age)`."
  - "`isfield(s, name)` asks whether a field exists; `s.(name)` reads a field whose name is in a variable."
---

A numeric array holds one type in a rectangle. When the things are not all the
same, you need something else.

## Cell arrays

```matlab
c = {1, 'two', [3 4 5]};
```

Each element is a container holding anything. The cost of that flexibility is
one extra layer, and the braces are how you get through it:

```matlab
c(2)     % a 1x1 CELL, still wrapped
c{2}     % 'two' - the contents
```

Almost every cell array bug is one of those where the other was meant. The
rule: **parentheses select, braces extract**. `c(1:2)` is a smaller cell array;
`c{1:2}` is a comma-separated list of two values, which is a different kind of
thing entirely and is why `x = c{1:2}` assigns only the first.

## What they are for

Text of differing lengths, above all:

```matlab
names = {'ada', 'grace', 'bob'};
```

A char *matrix* would have to pad every row to the same width. This is why
`readtable` hands back cell arrays of char for text columns, and why `cellfun`
exists.

`cellfun` with `'UniformOutput', false` returns a cell array; without it, one
number per element.

## Structs

```matlab
r.name = 'ada';
r.age = 36;
```

Named fields, each any type. `fieldnames(r)` lists them, `isfield(r, 'age')`
tests one, and `rmfield` removes one.

## Dynamic field names

```matlab
key = 'age';
r.(key)        % 36
```

The parentheses-after-dot form takes the field name from a variable. It is the
escape hatch when the field is not known until run time — and a sign that a
`containers.Map` or a table might fit better.

## Struct arrays

```matlab
people(1).name = 'ada';
people(2).name = 'bob';
[people.name]       % a comma-separated list, expanded into an array
{people.name}       % the same list, collected into a cell
```

Every element has the same fields. `people.name` produces a **list**, not an
array, which is why it needs `[ ]` or `{ }` around it to become one value.

A struct array is the shape a table replaces: same fields, many rows, but with
nothing keeping the lengths in step and no names on the columns.

## Your turn

- `count_type(c, className)` — how many elements of `c` have that class
- `longest(c)` — the longest char element, `''` when there are none
- `make_record(name, age)` — a struct with `name` and `age`
- `field_or(s, name, default)` — the field if present, otherwise `default`
