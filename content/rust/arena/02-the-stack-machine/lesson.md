---
title: "Round 2: The stack machine"
summary: Evaluate a tiny postfix language, and report exactly what went wrong when a program is bad.
order: 2
files: [src/lib.rs]
run: cargo test
challenge:
  minutes: 18
  xp: 200
  requires:
    xp: 900
---

The calculator firmware reads programs like `2 3 + 4 *`. Somebody has to
write the part that runs them.

## The task

In `src/lib.rs`, write `pub fn eval(program: &str) -> Result<i64, EvalError>`.
The error type is already in the file; do not change it.

A program is tokens separated by whitespace, run left to right against a
stack of `i64` values that starts empty.

| Token | What it does |
|---|---|
| an integer, such as `42` or `-7` | pushes it |
| `+` `-` `*` `/` | pops `b`, then pops `a`, and pushes `a + b`, `a - b`, `a * b` or `a / b` |
| `dup` | pushes a copy of the top value |
| `swap` | exchanges the top two values |
| `drop` | removes the top value |

When the program ends, the stack must hold exactly one value: that is the
result.

```text
eval("2 3 + 4 *")     ->  Ok(20)
eval("10 2 -")        ->  Ok(8)        (a is 10, b is 2)
eval("7 2 /")         ->  Ok(3)        (integer division)
eval("3 dup *")       ->  Ok(9)
```

What can go wrong, and the error for each:

- an operation needs more values than the stack has: `StackUnderflow`. So is
  a program that leaves the stack empty, including the empty program.
- dividing by zero: `DivisionByZero`
- a token that is none of the above: `UnknownToken` holding the token
- the program ends with more than one value on the stack: `LeftOver`
  holding how many values there are

Stop at the first error.
