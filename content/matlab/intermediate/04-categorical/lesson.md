---
title: categorical
summary: A fixed set of possible values, stored as small codes - which makes grouping exact instead of a guess from whatever text happened to appear.
order: 4
files: [to_sizes.m, most_common.m, at_least.m]
run: octave --no-gui --quiet --eval "disp(most_common({'red','blue','red'}))"
hints:
  - "`categorical(c)` infers the categories from the data and sorts them. `categorical(c, valueset)` fixes them instead."
  - "`categories(c)` lists them and `countcats(c)` counts each one, in the same order."
  - "`categorical(c, valueset, 'Ordinal', true)` makes < and > meaningful, in valueset order."
  - "`max` gives the position of the largest as its second output: `[~, at] = max(counts)`."
---

```matlab
colours = categorical({'red', 'blue', 'red'});
```

Each value is stored as a small integer code into one shared list of category
names. Two things follow.

**Memory**: a column of 100,000 city names becomes 100,000 codes plus one list,
not 100,000 separate char arrays.

**Exactness**: the set of possible values is *declared*, not inferred from
whichever rows you happen to have. A category with no rows still exists and
still counts zero, which is what makes two summaries from different samples
line up.

```matlab
categories(c)    % the names, in order
countcats(c)     % how many of each, in the same order
summary(c)
```

## Inferred against fixed

```matlab
categorical(c)                        % categories inferred, sorted
categorical(c, {'small','medium','large'})   % fixed, in this order
```

Fixing them is usually what you want. A value outside the set becomes
`<undefined>` rather than quietly inventing a new category — so a typo shows up
as missing data instead of as a category of one.

## Ordinal

```matlab
sizes = categorical(c, {'small','medium','large'}, 'Ordinal', true);
sizes > 'small'
```

Without `'Ordinal'`, `<` and `>` are **refused**. That is deliberate: for an
unordered categorical the position in the list is an implementation detail, not
a meaning, and comparing 'red' with 'blue' has no answer. Declaring it ordinal
is you saying the order is real.

The order comes from the **value set**, not from the alphabet — which is the
whole point, since small/medium/large does not sort alphabetically.

## Against plain text

A cell array of char can hold anything, so grouping it means trusting that
'London' and 'london ' are the same. A categorical decides that once, when it
is built.

This is why `readtable` columns are worth converting before you group them.

## Your turn

- `to_sizes(c)` — an ordinal categorical over `small`, `medium`, `large`
- `most_common(c)` — the most frequent value of a cell array of char, as a
  char array; ties go to the first alphabetically
- `at_least(sizes, ref)` — a logical mask of the entries at `ref` or above
