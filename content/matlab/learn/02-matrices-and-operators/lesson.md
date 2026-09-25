---
title: Matrices, and the dot that changes everything
summary: A * B is matrix multiplication and A .* B is element-wise. Confusing them is the most common MATLAB bug there is.
order: 2
files: [row_sums.m, scale_rows.m, is_symmetric.m, product_pair.m]
run: octave --no-gui --quiet --eval "disp(row_sums(magic(3)))"
hints:
  - "`sum(M)` adds down the columns. `sum(M, 2)` adds across the rows, and returns a column."
  - "`M .* factors(:)` multiplies row i by factors(i) - a column on the right broadcasts across the row dimension."
  - "`is_symmetric` compares M with its transpose: `isequal(M, M.')`."
  - "`product_pair` returns both results: `ew = A .* B;` and `mp = A * B;`."
---

```matlab
A * B      % matrix multiplication - rows into columns
A .* B     % element-wise - each entry times the matching entry
```

They are different operations that both compile, and for square matrices they
both **run**, producing different numbers with no warning. This is the most
common MATLAB bug there is, and the exam asks about it.

The dot means element-wise, and it applies across the family:

| | |
|---|---|
| `*` `/` `^` | matrix operations |
| `.*` `./` `.^` | element-wise |

`A^2` is `A*A`. `A.^2` squares each entry. For a 2×2 those are entirely
different matrices.

## Dimensions

`A * B` needs the columns of `A` to equal the rows of `B`, and gives
`rows(A) × cols(B)`. `A .* B` needs the shapes to match, or to be compatible
for broadcasting.

## Broadcasting

```matlab
M = [1 2; 3 4];
M .* [10; 100]     % row 1 times 10, row 2 times 100
M .* [10 100]      % column 1 times 10, column 2 times 100
```

A dimension of length 1 is stretched to fit. A **column** on the right scales
rows; a **row** scales columns. Which one you get depends on the orientation of
the vector, which is why `factors(:)` — forcing a column — is worth writing
even when you think you already have one.

This is implicit expansion, and it silently replaced an error in R2016b. Code
that used to fail now runs, which is convenient and occasionally hides a bug.

## Reductions take a dimension

```matlab
sum(M)        % down the columns - a row of column totals
sum(M, 1)     % the same thing, said explicitly
sum(M, 2)     % across the rows - a COLUMN of row totals
```

The default is **dimension 1**, down the columns. Every reduction works this
way: `mean`, `max`, `any`, `all`, `cumsum`. Writing the dimension explicitly
costs three characters and removes the doubt.

## Transpose

```matlab
A.'    % transpose
A'     % complex-conjugate transpose
```

They agree for real matrices and differ for complex ones. `.'` is the one that
means "flip it".

## Your turn

- `row_sums(M)` — the total of each row, as a column
- `scale_rows(M, factors)` — row `i` multiplied by `factors(i)`
- `is_symmetric(M)` — true when `M` equals its transpose
- `product_pair(A, B)` — returns `[element_wise, matrix_product]`
