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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **round** | a timed arena challenge |
| **bracket** | one of `( )`, `[ ]`, `{ }` |
| **opening** / **closing** bracket | `(`, `[`, `{` / `)`, `]`, `}` |
| **balanced** | every bracket closed by the right kind, in the right order |
| **wrong kind** | `(]`: closed by a different bracket |
| **wrong order** | `([)]`: the inner pair is closed after the outer one |
| **never closed** | an opening bracket with no partner by the end |
| **depth** | how deeply brackets sit inside each other, not how many pairs there are |
| **nest** | put one pair inside another |
| **-1** | here, the answer for "not balanced" |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Brackets.java && java Brackets` | builds and runs this round's file |

### Java names

| Name | What it does |
|---|---|
| `static boolean balanced(String s)` | the first method to write |
| `static int depth(String s)` | the second |
| `s.charAt(i)`, `s.length()` | one character; the number of characters |
| `for (char c : s.toCharArray())` | each character in turn |
| `switch (c) { case '(' -> ...; }` | choose by character |
| `Math.max(a, b)` | the larger of two numbers |

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

Depth counts how deeply brackets sit inside each other, not how many pairs
there are: `"()[]"` is two pairs side by side, depth 1, while `"{[(())]}"` is
depth 4. Both methods must cope with a long line too: one test nests 5,000
brackets inside each other.
