---
title: Arrays, multidimensional arrays and varargs
summary: Fixed length, default values, the Arrays helper methods, and why comparing two arrays with equals does not do what you want.
order: 4
files: [Arrays2.java]
run: javac Arrays2.java && java Arrays2
hints:
  - "`sum(int... values)` is varargs: inside the method `values` IS an int[], so a plain enhanced for works. Calling it with no arguments gives an empty array, not null."
  - "`largest` should throw IllegalArgumentException on an empty array rather than returning 0 - there is no largest element of nothing."
  - "`copyWithout` is easiest in two passes: count the survivors, allocate an array of exactly that size, then fill it."
  - "`grid(rows, cols)` returns int[rows][cols] where each cell is row * cols + col. A nested loop, outer over rows."
---

An array in Java has a **fixed length**, decided when it is created and never
changed.

```java
int[] a = new int[3];              // [0, 0, 0] - never null elements for primitives
int[] b = {1, 2, 3};               // literal form
String[] s = new String[2];        // [null, null]
```

Elements get the type's default: `0` for numeric types, `false` for boolean,
`'\u0000'` for char, and `null` for any reference type. There is no such thing
as an uninitialised array element.

`length` is a **field**, not a method: `a.length`, no parentheses. Strings use
`length()`. Mixing them up is the exam's favourite one-character trap.

Indices run `0` to `length - 1`; anything else throws
`ArrayIndexOutOfBoundsException` at runtime. The compiler does not catch it
even for an obvious constant.

## Arrays helpers

```java
import java.util.Arrays;

Arrays.toString(a)        // "[1, 2, 3]" - printing an array directly gives [I@1b6d
Arrays.sort(a)            // sorts IN PLACE, returns void
Arrays.copyOf(a, 5)       // a longer copy, padded with defaults
Arrays.equals(a, b)       // element by element
Arrays.fill(a, 7)
```

Two of these matter more than the rest:

- **`a.equals(b)` compares references**, so two arrays with identical contents
  are not equal. `Arrays.equals(a, b)` is what you meant. For nested arrays,
  `Arrays.deepEquals`.
- **`System.out.println(a)` prints something like `[I@6d06d69c`** — the type
  and a hash, not the contents. `Arrays.toString(a)` is what you want.

## Multidimensional

```java
int[][] grid = new int[3][4];      // 3 rows, 4 columns
int[][] ragged = new int[3][];     // rows allocated separately, may differ in length
```

Java has no true 2D array: `int[][]` is an array **of arrays**, which is why
rows can have different lengths. `grid.length` is the row count;
`grid[0].length` is that row's width.

## Varargs

```java
public static int sum(int... values)
```

Inside the method, `values` is an ordinary `int[]`. The caller can pass any
number of arguments, including none — which gives an empty array, never null.
Varargs must be the **last** parameter, and a method can have only one.

## Your turn

In `Arrays2.java`:

- `public static int sum(int... values)` — 0 for no arguments
- `public static int largest(int[] values)` — throws
  `IllegalArgumentException` for an empty array
- `public static int[] copyWithout(int[] values, int unwanted)` — a new array
  with every occurrence removed
- `public static int[][] grid(int rows, int cols)` — cell `[r][c]` holds
  `r * cols + c`
