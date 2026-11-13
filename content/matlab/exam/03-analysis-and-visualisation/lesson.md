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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **descriptive statistics** | summaries such as mean, median and spread |
| **mean** / **median** | average / middle value, which outliers do not pull |
| **skew** | values bunched to one side |
| **sample standard deviation** | divides by `n-1`; `std` does this by default |
| **population standard deviation** | divides by `n`: `std(v, 1)` |
| **range** | `max - min` |
| **reduction** | an operation that collapses a dimension, such as `mean` |
| **reduction dimension** | `mean(M)` goes down the columns, giving a row |
| **figure** | a window or image holding a chart |
| **axis labels** | the text naming each axis; a figure needs them |
| **PNG** | an image file format |
| **headless figure** | made with `'visible', 'off'` and saved with `print` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `mean`, `median`, `std`, `max`, `min` | the statistics |
| `mean(M(:))` | the mean of every element |
| `sortrows(t, varName, 'descend')` | sorts whole table rows, largest first |
| `t(1:min(n, height(t)), :)` | the first `n` rows, or fewer |
| `figure('visible', 'off')` | a figure with no window |
| `bar(values)` | a bar chart |
| `xticklabels(labels)`, `xlabel`, `ylabel`, `title` | labels |
| `print(f, filename, '-dpng')` | saves the figure as a PNG |
| `close(f)` | closes the figure |
| `nargin` | how many arguments were passed, for the optional `labels` |

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

The first three rules, as numbers:

```matlab
v = [1 2 3 4 100];
fprintf('mean %g, median %g\n', mean(v), median(v));
fprintf('sample %.4f, population %.4f\n', std([1 2 3 4]), std([1 2 3 4], 1));
M = [1 2; 3 4];
disp(mean(M))
disp(mean(M(:)))
```

```output
mean 22, median 3
sample 1.2910, population 1.1180
2 3
2.5000
```

## Your turn

- `summary_stats(v)` — a struct with `avg`, `med`, `sd` and `rng`
  (`max - min`). Throws `summary_stats:empty` for an empty input.
- `top_n(t, varName, n)` — the `n` rows with the largest value of `varName`,
  ordered largest first. Fewer than `n` rows is not an error.
- `save_bar(filename, values, labels)` — a labelled bar chart written as a PNG.
  `labels` may be omitted.
