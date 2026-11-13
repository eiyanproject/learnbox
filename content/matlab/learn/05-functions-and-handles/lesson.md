---
title: Function handles
summary: A function you can pass around, an anonymous function you can write inline, and the fact that it captures its variables the moment you create it.
order: 5
files: [apply_twice.m, make_adder.m, apply_all.m]
run: octave --no-gui --quiet --eval "add5 = make_adder(5); disp(add5(10))"
hints:
  - "`@sin` is a handle to an existing function. `@(x) x.^2` is an anonymous one written on the spot."
  - "Call a handle like any function: `f(x)`. `apply_twice` is one line - `out = f(f(x));`."
  - "`make_adder` returns a handle: `adder = @(x) x + n;`. The n is captured when the handle is made."
  - "`arrayfun(f, v)` applies f to each element and collects the results."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **function handle** | a function stored as a value |
| **named handle** | `@sin`: a handle to an existing function |
| **anonymous function** | `@(x) x.^2 + 1`: written in place; one expression only |
| **capture at creation** | an anonymous function freezes the values it uses when built |
| **capture by reference** | what some other languages do; MATLAB does not |
| **uniform output** | one number back per element, collected into an array |
| **higher-order function** | one that takes or returns a function |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `h = @sin; h(0)` | a handle, and calling it |
| `g = @(x) x.^2 + 1;` | an anonymous function |
| `arrayfun(f, v)` | applies `f` to each element of an array |
| `cellfun(f, c, 'UniformOutput', false)` | applies `f` to each cell, giving a cell array |
| `function out = apply_twice(f, x)` | a function taking a function |
| `fzero`, `integral`, `ode45` | built-ins that take your function as an argument |

### Errors

| Error | Means |
|---|---|
| `Non-scalar in Uniform output` | `arrayfun`/`cellfun` got something other than one number; add `'UniformOutput', false` |

---

## Two kinds of handle

```matlab
h = @sin;               % a handle to a function that already exists
g = @(x) x.^2 + 1;      % an anonymous function, written here
```

Both are values. They go in variables, into arrays, into other functions, and
out of them. `h(0)` calls it.

An anonymous function's body is **one expression**. No statements, no `if`, no
loop. If you need those, write a real function — that restriction is deliberate
and keeps anonymous functions readable.

## Capture happens at creation

```matlab
n = 5;
add = @(x) x + n;
n = 100;
add(1)        % 6, not 101
```

The value of `n` is frozen into the handle when the handle is built. Later
changes to `n` do not reach it, and the handle keeps that value alive even
after `n` is cleared.

This is the opposite of what people expect from languages that capture by
reference, and it is examined. It is also what makes `make_adder` work at all:
the returned handle carries its own `n` after the function has returned.

## Applying one to many

```matlab
arrayfun(@(x) x * 2, [1 2 3])                        % 2 4 6
cellfun(@upper, {'a', 'b'}, 'UniformOutput', false)  % {'A', 'B'}
```

Both apply a function to each element. The default is to expect **one number
back per element** and to collect them into an array. When the result is not a
scalar — text, a vector, anything — you need `'UniformOutput', false`, and you
get a cell array back.

The error when you forget is *"Non-scalar in Uniform output"*, and now you know
what it means.

For plain arithmetic, a vectorised expression beats `arrayfun`: `v * 2` is
clearer and faster than `arrayfun(@(x) x * 2, v)`. Reach for these when the
operation genuinely is a function.

## Passing functions in

```matlab
function out = apply_twice(f, x)
  out = f(f(x));
end
```

The caller decides what `f` is. That is the whole idea, and it is how `fzero`,
`integral`, `ode45` and `arrayfun` all take your code as an argument.

## All of it, run

```matlab
n = 5;
add = @(x) x + n;
n = 100;
disp(add(1))
disp(arrayfun(@(x) x * 2, [1 2 3]))
c = cellfun(@upper, {'a', 'b'}, 'UniformOutput', false);
disp(class(c))
fprintf('%s %s\n', c{:});
twice = @(f, x) f(f(x));
disp(twice(@(x) x * 3, 2))
```

```output
6
2 4 6
cell
A B
18
```

## Your turn

- `apply_twice(f, x)` — `f` applied to `x`, twice
- `make_adder(n)` — returns a handle that adds `n`
- `apply_all(f, v)` — `f` applied to each element of `v`
