---
title: "Round 1: Brackets"
summary: Decide whether the brackets in a line of code match up, and how deep they go.
order: 1
files: [Brackets.java]
run: javac Brackets.java && java Brackets
challenge:
  minutes: 12
  xp: 150
  requires:
    xp: 250
---

The editor's bracket checker is broken and the release is this afternoon.

## The task

In `Brackets.java`, write two static methods.

`boolean balanced(String s)` is `true` when every bracket in `s` is closed by
the right kind of bracket in the right order. The brackets are `()`, `[]`
and `{}`. Every other character is ignored.

```text
balanced("(a[0] + {b})")   ->  true
balanced("")               ->  true
balanced("(]")             ->  false   (wrong kind)
balanced("([)]")           ->  false   (wrong order)
balanced("((")             ->  false   (never closed)
balanced(")(")             ->  false   (closed before it was opened)
```

`int depth(String s)` is the deepest the brackets nest, or `-1` if they are
not balanced.

```text
depth("abc")           ->  0
depth("()[]")          ->  1
depth("f(a[i], {x})")  ->  2
depth("(]")            ->  -1
```
