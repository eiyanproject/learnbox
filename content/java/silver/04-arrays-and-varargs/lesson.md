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

An **array** holds a numbered row of values, all of the same type: ten
scores, a week of temperatures, the cells of a board. It is the most basic
collection in Java, and the fastest, because its elements sit side by side in
memory. The price is that an array in Java has a **fixed length**, decided
when it is created and never changed. For a collection that grows, Java has
`ArrayList` (the Core APIs lesson); arrays are what it is built on.

```java
int[] a = new int[3];              // [0, 0, 0] - never null elements for primitives
int[] b = {1, 2, 3};               // literal form
String[] s = new String[2];        // [null, null]
```

(A fragment: lines from inside a method.) `int[]` is the type "array of
`int`". `new int[3]` creates an array of three; `{1, 2, 3}` creates one
holding those values, with its length taken from how many there are. The
elements are reached by position, from 0: `b[0]` is `1`, and `b[2] = 9;`
replaces the last one.

Elements get the type's default: `0` for numeric types, `false` for boolean,
`'\u0000'` for char, and `null` for any reference type. There is no such thing
as an uninitialised array element.

`length` is a **field**, not a method: `a.length`, no parentheses. Strings use
`length()`. Mixing them up is the exam's favourite one-character trap.

Why start at 0? An array's elements sit one after another in memory, and
the variable refers to where the first one begins. An index is an
**offset**: `a[0]` means "the start, moved along by 0 elements", `a[2]`
"moved along by 2". Counting from the start in steps is why the first
element is 0 and the last is `length - 1`.

Indices run `0` to `length - 1`; anything else throws
`ArrayIndexOutOfBoundsException` at runtime. The compiler does not catch it
even for an obvious constant: `z[2] = 1` on an array of length 2 compiles
cleanly and fails only when that line runs (the program below shows the
message). Array bounds are a run-time check, not a compile-time one.

## Arrays helpers

Arrays have almost no methods of their own. The `java.util.Arrays` class
supplies them instead, as static methods that take the array as an argument:

```java
import java.util.Arrays;

Arrays.toString(a)        // "[1, 2, 3]" - printing an array directly gives [I@1b6d
Arrays.sort(a)            // sorts IN PLACE, returns void
Arrays.copyOf(a, 5)       // a longer copy, padded with defaults
Arrays.equals(a, b)       // element by element
Arrays.fill(a, 7)         // sets every element to 7
```

(Calls with what they do; the program below runs several of them.)
`copyOf` is also how you "resize" an array: you cannot, so you make a new one
of the size you want and copy the old elements in.

Two of these matter more than the rest:

- **`a.equals(b)` compares references**, so two arrays with identical contents
  are not equal. `Arrays.equals(a, b)` is what you meant. For nested arrays,
  `Arrays.deepEquals`.
- **`System.out.println(a)` prints something like `[I@6d06d69c`** — the type
  and a hash, not the contents. `[I` is the JVM's internal name for "array of
  `int`", and the part after `@` is a number derived from the object's
  identity. `Arrays.toString(a)` is what you want.

Both come from the same fact: an array is an object, but it does not override
`equals` or `toString`, so it gets the default versions from `Object`, which
look at identity, not contents.

## Multidimensional

```java
int[][] grid = new int[3][4];      // 3 rows, 4 columns
int[][] ragged = new int[3][];     // rows allocated separately, may differ in length
```

Java has no true 2D array: `int[][]` is an array **of arrays**, which is why
rows can have different lengths. `grid.length` is the row count;
`grid[0].length` is that row's width. `grid[1][2]` reads row 1, then position
2 within that row. `new int[3][4]` creates the outer array and all three rows
in one go; `new int[3][]` creates only the outer array, with each row `null`
until you assign one, such as `ragged[0] = new int[5];`.

## Varargs

```java
public static int sum(int... values)
```

**Varargs** (variable arguments), written as the type followed by `...`, lets
a method take any number of values of that type. Inside the method, `values`
is an ordinary `int[]`. The caller can pass any number of arguments, including
none — which gives an empty array, never null — or pass an existing array
directly: `sum(1, 2, 3)` and `sum(new int[] {1, 2, 3})` are the same call.
Varargs must be the **last** parameter, and a method can have only one;
otherwise Java could not tell where the variable part ends.
`String.format(String format, Object... args)` is a varargs method you will
use often.

## Run

```java
import java.util.Arrays;

public class ArraysDemo {
    public static void main(String[] args) {
        int[] a = new int[3];
        String[] s = new String[2];
        System.out.println(Arrays.toString(a) + " " + Arrays.toString(s));

        int[] x = {3, 1, 2};
        int[] y = {3, 1, 2};
        System.out.println(x.equals(y) + " " + Arrays.equals(x, y));
        Arrays.sort(x);
        System.out.println(Arrays.toString(Arrays.copyOf(x, 5)));
        System.out.println(String.valueOf(x).startsWith("[I@"));   // what println(x) shows

        int[][] ragged = {{1}, {2, 3, 4}};
        System.out.println(ragged.length + " " + ragged[1].length);
        System.out.println(sum() + " " + sum(1, 2, 3));

        try {
            int[] z = new int[2];
            z[2] = 1;
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println(e.getMessage());
        }
    }

    static int sum(int... values) {
        int total = 0;
        for (int v : values) total += v;
        return total;
    }
}
```

```output
[0, 0, 0] [null, null]
false true
[1, 2, 3, 0, 0]
true
2 3
0 6
Index 2 out of bounds for length 2
```

In order: new arrays hold the defaults; `equals` on two arrays with the same
contents is `false` (different objects) while `Arrays.equals` is `true`;
`sort` changed `x` itself, and `copyOf` padded the copy to five with zeros;
the default text for an array starts with `[I@`; the ragged array has 2 rows,
the second of length 3; varargs called with nothing gives 0; and writing to
index 2 of a two-element array throws, caught here by `try`/`catch` (the
Exceptions lesson) so the message can be printed.

## Your turn

In `Arrays2.java`:

- `public static int sum(int... values)` — the total, 0 for no arguments
- `public static int largest(int[] values)` — the biggest element, correct for
  all-negative arrays too (`{-5, -2, -9}` gives `-2`, so do not start from 0).
  Throws `IllegalArgumentException` for an empty array, since nothing has no
  largest element: `throw new IllegalArgumentException("empty array");`
- `public static int[] copyWithout(int[] values, int unwanted)` — a new array
  with every occurrence of `unwanted` removed, exactly as long as the values
  that remain (`{1, 2, 3, 2}` without 2 is `{1, 3}`, length 2; removing
  everything gives a length-0 array). Do not change the array you were given.
- `public static int[][] grid(int rows, int cols)` — `rows` rows of `cols`
  cells each, where cell `[r][c]` holds `r * cols + c`: `grid(2, 3)` is
  `{{0, 1, 2}, {3, 4, 5}}`. Each row must be its own array.
