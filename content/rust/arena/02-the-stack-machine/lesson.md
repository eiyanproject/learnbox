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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **stack machine** | a calculator that runs a program of tokens against a stack |
| **stack** | values where the last one pushed is the first one popped |
| **push** / **pop** | put a value on top / take the top value off |
| **token** | one word of the program, separated by whitespace |
| **postfix notation** | operators after their operands: `2 3 +` |
| **`a` and `b`** | for an operator, `b` is popped first, then `a`, and the result is `a op b` |
| **`dup`**, **`swap`**, **`drop`** | copy the top; exchange the top two; remove the top |
| **stack underflow** | an operation needs more values than the stack has |
| **left over** | more than one value at the end |
| **first error** | the one found first in reading order |
| **integer division** | rounds toward zero: `-7 2 /` is `-3` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs this round's tests |

### Rust names

| Name | What it does |
|---|---|
| `pub fn eval(program: &str) -> Result<i64, EvalError>` | the function to write |
| `EvalError::StackUnderflow`, `DivisionByZero`, `UnknownToken(String)`, `LeftOver(usize)` | the given error type |
| `program.split_whitespace()` | the tokens, splitting on any whitespace |
| `token.parse::<i64>()` | try the token as a number first, so `-2` is a number |
| `let mut stack: Vec<i64> = Vec::new();`, `stack.push(x)`, `stack.pop()` | the stack |
| `stack.pop().ok_or(EvalError::StackUnderflow)?` | pop, or fail |
| `stack.last().copied()` | the top value without removing it |
| `match token { "+" => ..., "dup" => ..., _ => ... }` | choose by token |

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

## Details the tests check

- `-` on its own is the subtraction operator, but `-2` is the number minus
  two: `eval("5 3 - -2 -")` is `Ok(4)`. Trying `token.parse::<i64>()` first,
  and treating the token as an operator only if that fails, handles this.
- Division rounds toward zero, like Rust's `/` on integers:
  `eval("-7 2 /")` is `Ok(-3)`.
- Only whole numbers are numbers: `1.5` is `UnknownToken("1.5")`.
- The words are lower-case: `DUP` is `UnknownToken("DUP")`.
- Any whitespace separates tokens, tabs and newlines included.
- "First error" means first in reading order: `"+ nonsense"` is
  `StackUnderflow`, because `+` fails before `nonsense` is reached, while
  `"nonsense +"` is `UnknownToken("nonsense")`.
