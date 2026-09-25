---
title: Plotting
summary: Build the data, draw it, label it, and save it to a file - which is how a plot is produced when there is no screen to draw on.
order: 6
files: [sine_data.m, save_plot.m]
run: octave --no-gui --quiet --eval "[x,y] = sine_data(50); save_plot('wave.png', x, y, 'a sine wave'); disp('wrote wave.png')"
hints:
  - "`linspace(0, 2*pi, n)` gives n points including both endpoints - that is why it is right here and `0:2*pi` is not."
  - "`figure('visible', 'off')` makes a figure without needing a screen. There is no display in this container."
  - "Label everything: `xlabel`, `ylabel`, `title`, and `grid on`. An unlabelled plot is not a finished plot."
  - "`print(filename, '-dpng')` writes the current figure to a file. Close it afterwards with `close(f)` so figures do not pile up."
---

## The data comes first

```matlab
x = linspace(0, 2*pi, 200);
y = sin(x);
```

`linspace(a, b, n)` gives `n` points with both endpoints included. That is the
difference from `0:0.1:2*pi`, which guarantees the step and lets the last point
fall wherever it falls — often just short of `2*pi`.

Keeping the data separate from the drawing is worth doing for its own sake: you
can test the numbers, and you can draw them more than one way.

## Drawing

```matlab
f = figure('visible', 'off');
plot(x, y);
xlabel('x');
ylabel('sin(x)');
title('a sine wave');
grid on;
```

`plot(x, y)` draws a line through the points. Related calls:

| | |
|---|---|
| `scatter(x, y)` | points, no line |
| `bar(values)` | bars |
| `histogram(v)` | distribution |
| `hold on` | draw the next one on top instead of replacing |

`hold on` is the one people miss. Without it, the second `plot` **replaces**
the first.

## Labels are not decoration

An axis without a label is a graph of nothing. `xlabel`, `ylabel`, `title`, and
`legend` when there is more than one line — the exam asks about these, and so
does anybody reading your figure.

## Saving

```matlab
print('wave.png', '-dpng');
close(f);
```

`print` writes the current figure to a file; `-dpng` picks the format. There is
no screen in this container, so `'visible', 'off'` and `print` are the whole
workflow — and they are also exactly what you want in a script that produces
figures unattended.

Closing matters. Figures accumulate, each holding its data, and a loop that
draws a hundred without closing them will run the process out of memory.

## Your turn

- `sine_data(n)` — returns `[x, y]` for one full period of sine, `n` points
- `save_plot(filename, x, y, titleText)` — draws, labels and saves a PNG
