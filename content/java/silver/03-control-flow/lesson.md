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

## if, and the ternary

```java
String label = score >= 50 ? "pass" : "fail";
```

The ternary is an **expression**: it produces a value. `if` is a statement and
does not. That distinction is why the ternary can go inside a method call and
`if` cannot.

Java requires a `boolean` in every condition. There is no truthiness: `if (1)`
does not compile, and `if (x = 5)` — the classic accidental assignment — does
not compile either unless `x` is a boolean. The type system removes a whole
family of C bugs.

## switch: the old form fell through

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

Fall-through is deliberate — stacking `case 6:` and `case 7:` relies on it —
but a forgotten `break` is a silent bug, and the exam uses it constantly.
Trace every case to the next `break` when you read one.

## switch expressions

Since Java 14 the arrow form both returns a value and cannot fall through:

```java
String type = switch (day) {
    case SATURDAY, SUNDAY -> "weekend";
    default -> "weekday";
};
```

Three improvements at once: no `break`, several labels per arm, and it is an
expression so the result can be assigned. When an arm needs several statements,
use a block and `yield`:

```java
case 1 -> { int x = compute(); yield x * 2; }
```

A switch **expression** must be exhaustive — every possible value covered, or a
`default`. A switch **statement** need not be.

## Loops

`for`, `while`, `do-while` (which always runs at least once), and the enhanced
for:

```java
for (String s : items) { ... }
```

The enhanced for gives you the element, not the index, and you cannot assign
through it to change the array. Use a classic `for` when you need the position.

`break` leaves the loop, `continue` skips to the next iteration. Both take a
label to act on an outer loop:

```java
outer:
for (...) { for (...) { if (found) break outer; } }
```

Labels are the one legitimate use of anything goto-shaped in Java, and they
exist precisely so you do not need a flag variable.

## Your turn

In `Flow.java`:

- `public static String grade(int score)` — `"A"` at 90+, `"B"` 80+, `"C"` 70+,
  `"D"` 60+, otherwise `"F"`
- `public static String dayType(int day)` — 1-5 `"weekday"`, 6-7 `"weekend"`,
  anything else `"invalid"`, written as a switch
- `public static int firstMultiple(int[] values, int n)` — first value
  divisible by `n`, or -1
- `public static String countdown(int from)` — `3` gives `"3,2,1"`, and 0 or
  less gives `""`
