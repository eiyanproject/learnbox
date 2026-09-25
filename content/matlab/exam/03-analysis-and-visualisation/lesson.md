---
title: "Paper 3: analysis and visualisation"
summary: Summarising numbers, ranking rows, and producing a figure somebody else can read.
order: 3
files: [summary_stats.m, top_n.m, save_bar.m]
run: octave --no-gui --quiet --eval "save_bar('chart.png', [3 1 2], {'a','b','c'}); disp('wrote chart.png')"
hints:
  - "`median` is not `mean`, and the range is `max(v) - min(v)`."
  - "`sortrows(t, var, 'descend')` then take the first n - and n may be larger than the table."
  - "`set(gca, 'xtick', 1:numel(values), 'xticklabel', labels)` puts the labels under the bars."
---

The third paper covers the **analysis and visualisation** domain: descriptive
statistics, ordering, and figures.

Worth having straight:

- `mean` is pulled by outliers and `median` is not; quoting one without the
  other hides skew
- `std` divides by `n-1` by default — the sample standard deviation
- reductions take a dimension: `mean(M)` goes down the columns
- a figure with no axis labels is not a finished figure
- `'visible', 'off'` plus `print` is how a figure is made without a screen

Two traps this domain is fond of.

**The reduction dimension.** `mean(M)` on a matrix gives a *row* of column
means, not one number. If you wanted the overall mean you wanted `mean(M(:))`,
and the difference does not announce itself — both are perfectly good numbers.

**Sorting one column.** Ordering a matrix by one of its columns, without
carrying the others along, destroys the correspondence between them silently.
`sortrows` on a table moves whole rows, which is why it is the right tool even
when the data would fit in a matrix.

## Your turn

- `summary_stats(v)` — a struct with `avg`, `med`, `sd` and `rng`
  (`max - min`). Throws `summary_stats:empty` for an empty input.
- `top_n(t, varName, n)` — the `n` rows with the largest value of `varName`,
  ordered largest first. Fewer than `n` rows is not an error.
- `save_bar(filename, values, labels)` — a labelled bar chart written as a PNG.
  `labels` may be omitted.
