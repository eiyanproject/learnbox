---
title: Control flow and switch
summary: if and the ternary, the switch statement's fall-through, the switch expression that fixed it, and loop control with labels.
order: 3
files: [Flow.java]
run: javac Flow.java && java Flow
hints:
  - "`grade` is a ladder of if/else. Check the highest boundary first, or every score falls into the first branch that matches loosely."
  - "`dayType` is the switch: use an arrow switch expression (`case SATURDAY, SUNDAY -> \"weekend\";`) and you cannot fall through by accident."
  - "`firstMultiple` returns the first value in the array divisible by n, or -1. A plain loop with an early `return` is the clearest form."
  - "`countdown` builds \"3,2,1\" - append the separator between items, not after each, or you get a trailing comma."
---

A program that always runs the same lines in the same order cannot react to
anything. **Control flow** is how it chooses: run this block only if a
condition holds, pick one of several branches by value, repeat until done.
Java's tools for this look like C's, but two of them, `switch` and the label
on a loop, have behaviour the exam tests in detail, and the newer switch
*expression* fixes a decades-old trap of the older form.

## if, and the ternary

`if (condition) { ... } else { ... }` runs one block or the other. The
**ternary** operator, `condition ? a : b`, is the same choice in a form that
produces a value: `a` if the condition is true, otherwise `b`:

```java
String label = score >= 50 ? "pass" : "fail";
```

(A fragment: `score` is an `int` defined elsewhere.) This does the same as:

```java
String label;
if (score >= 50) {
    label = "pass";
} else {
    label = "fail";
}
```

The ternary is an **expression**: it produces a value. `if` is a statement and
does not. That distinction is why the ternary can go inside a method call,
as in `System.out.println(n > 0 ? "positive" : "not positive")`, and `if`
cannot.

### The order of an if/else ladder is the logic

An `if` / `else if` chain runs the **first** branch whose condition is true
and skips the rest. That makes the order of the conditions part of the
meaning. Here is a grading ladder with the checks written in the "natural"
order, lowest first, run on three scores:

```java
public class Ladder {
    static String grade(int score) {
        if (score >= 50) {
            return "pass";
        } else if (score >= 70) {          // never reached for 70 or more...
            return "merit";
        } else if (score >= 90) {          // ...and neither is this
            return "distinction";
        }
        return "fail";
    }

    public static void main(String[] args) {
        System.out.println(grade(95));      // expected distinction
        System.out.println(grade(75));      // expected merit
        System.out.println(grade(40));
    }
}
```

```output
pass
pass
fail
```

95 is at least 50, so the first branch matches and the other two are never
looked at. Every score from 50 up is a "pass". The fix is to test the most
demanding condition first: `>= 90`, then `>= 70`, then `>= 50`. Then each
later branch may safely assume the earlier ones failed: by the time
`>= 70` is checked, the score is already known to be below 90. This
lesson's `grade` exercise has exactly this shape.

Java requires a `boolean` in every condition. There is no **truthiness**
(treating 0, empty strings or null as false, as Python and JavaScript do):
`if (1)` does not compile, and `if (x = 5)` — the classic accidental
assignment — does not compile either unless `x` is a boolean. Both fail with
`incompatible types: int cannot be converted to boolean`. The type system
removes a whole family of C bugs.

## switch: the old form fell through

A `switch` compares one value against a list of constants, the `case`
labels, and jumps to the one that matches. `default` is where it goes if none
do. It works on `int` and the smaller integer types, `char`, `String` and
enums (and, since Java 21, on objects by type, which is beyond this lesson).

```java
switch (day) {
    case 6:
    case 7:
        type = "weekend";
        break;          // without this, execution continues into the next case
    default:
        type = "weekday";
}
```

A `case` label is only a place to *start*. Once Java jumps there, it runs
every line below it, straight through the following labels, until it meets a
`break` (or the end of the `switch`). That is **fall-through**. Here, day 6
jumps to `case 6:`, finds no code there, falls into `case 7:`'s lines, sets
"weekend", and the `break` stops it before `default`.

Fall-through is deliberate — stacking `case 6:` and `case 7:` relies on it —
but a forgotten `break` is a silent bug, and the exam uses it constantly.
Trace every case to the next `break` when you read one; the program at the
end of the lesson has a missing `break` on purpose.

## switch expressions

Since Java 14 the arrow form both returns a value and cannot fall through:

```java
String type = switch (day) {
    case SATURDAY, SUNDAY -> "weekend";
    default -> "weekday";
};
```

(A fragment: `day` is a `DayOfWeek`, an enum of the seven days, so the
labels are its constants.)

Three improvements at once: no `break`, several labels per arm, and it is an
expression so the result can be assigned. Each `case ... ->` line is an
**arm**: the labels before the arrow, and the value after it. Only the
matching arm runs; there is nothing to fall into.

The two forms side by side, doing the same job. The old form needs a
variable declared first, an assignment in each case, and a `break` after
each; the essence, "Saturday and Sunday are the weekend", is buried in the
ceremony around it. The new form says only that:

```java
// statement: assigns in each case, and needs every break
String type;
switch (day) {
    case SATURDAY:
    case SUNDAY:
        type = "weekend";
        break;
    default:
        type = "weekday";
}

// expression: produces the value directly
String type = switch (day) {
    case SATURDAY, SUNDAY -> "weekend";
    default -> "weekday";
};
```

When an arm needs several statements, use a block and `yield`, which gives
the value the block produces (like `return`, but for the switch rather than
the method):

```java
case 1 -> { int x = compute(); yield x * 2; }
```

A switch **expression** must be exhaustive — every possible value covered, or a
`default` — because it must produce a value whatever the input. Leaving one
out is a compile error (`the switch expression does not cover all possible
input values`). A switch **statement** need not be: if nothing matches, it
simply does nothing.

## Loops

Java has four loops:

- `for (int i = 0; i < n; i++) { ... }`, the classic counting loop: a start
  (`int i = 0`), a condition checked before every round (`i < n`), and a step
  run after every round (`i++`, add one to `i`).
- `while (condition) { ... }`, which checks the condition before every round,
  so it may run zero times.
- `do { ... } while (condition);`, which checks *after* every round, so it
  always runs at least once.
- the **enhanced for**, which visits each element of an array or collection:

```java
for (String s : items) { ... }
```

(Read the colon as "in": for each `s` in `items`.) The enhanced for gives you
the element, not the index, and you cannot assign through it to change the
array: `s = "x";` inside the loop only changes the loop variable, not the
array's slot. Use a classic `for` when you need the position.

When a loop is hard to follow, trace it: draw a table with a column for each
variable and for the condition, and write one row each time the condition is
checked. For this loop, which adds up 3 four times:

```java
int result = 0;
for (int i = 0; i < 4; i++) {
    result += 3;
}
```

| `result` | `i` | `i < 4` |
|---|---|---|
| 0 | 0 | true |
| 3 | 1 | true |
| 6 | 2 | true |
| 9 | 3 | true |
| 12 | 4 | false: the loop ends |

The last row shows two things worth knowing: the condition is checked one
more time than the body runs, and `i` ends at 4, one past the last value the
body saw.

`break` leaves the loop, `continue` skips to the next iteration. Both take a
**label**, a name followed by a colon written in front of a loop, to act on an
outer loop instead of the innermost one:

```java
outer:
for (...) { for (...) { if (found) break outer; } }
```

(A sketch: the `...` stand for real loop headers.) A plain `break` inside the
inner loop would only leave the inner loop, and the outer one would carry on.
`break outer` leaves both at once. Labels are the one legitimate use of
anything goto-shaped in Java, and they exist precisely so you do not need a
flag variable.

## Traced

```java
public class Flow {
    public static void main(String[] args) {
        for (int day : new int[] {5, 6}) {
            String type = "unset";
            switch (day) {
                case 5:
                    type = "friday";          // no break: falls into case 6
                case 6:
                    type = type + "+weekend";
                    break;
                default:
                    type = "weekday";
            }
            System.out.println(day + " " + type);
        }

        int n = 0;
        do { n++; } while (n < 0);            // false at once, but the body ran
        System.out.println("do-while ran " + n);

        String found = "none";
        outer:
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (i * j == 2) { found = i + "," + j; break outer; }
            }
        }
        System.out.println(found);

        int score = 72;
        System.out.println(switch (score / 10) {
            case 9, 10 -> "A";
            case 7, 8 -> "B";
            default -> "C";
        });
    }
}
```

```output
5 friday+weekend
6 unset+weekend
do-while ran 1
1,2
B
```

Tracing each line:

- Day 5 matches `case 5:`, sets `"friday"`, and with no `break` falls into
  `case 6:`, which adds `"+weekend"`. Day 6 jumps straight to `case 6:`, so
  `type` still holds its starting value, `"unset"`. That is the missing
  `break` at work.
- The `do-while` condition `n < 0` is false the first time it is checked, but
  by then the body has already run once.
- The nested loops reach `i * j == 2` first at `i = 1, j = 2`, and
  `break outer` stops both loops there.
- `72 / 10` is `7` (integer division), which matches `case 7, 8`.

`new int[] {5, 6}` creates an array with those two values on the spot, for
the loop to run over.

## Your turn

In `Flow.java`:

- `public static String grade(int score)` — `"A"` at 90 or more, `"B"` at 80
  or more, `"C"` at 70 or more, `"D"` at 60 or more, otherwise `"F"`. So 90 is
  an `"A"` and 89 a `"B"`.
- `public static String dayType(int day)` — 1-5 `"weekday"`, 6-7 `"weekend"`,
  anything else (0, 8, ...) `"invalid"`, written as a switch
- `public static int firstMultiple(int[] values, int n)` — the first value, in
  array order, that `n` divides exactly, or -1 if none does (including for an
  empty array). "First" means earliest, not smallest:
  `firstMultiple(new int[] {6, 4}, 2)` is `6`.
- `public static String countdown(int from)` — the numbers from `from` down
  to 1, separated by commas, with no comma at the end: `3` gives `"3,2,1"`,
  `1` gives `"1"`, and 0 or less gives `""`
