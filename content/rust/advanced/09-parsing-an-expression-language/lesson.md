---
title: A tokenizer and parser
summary: Turn text into tokens, tokens into a syntax tree with recursive descent and operator precedence, and report errors with positions.
order: 9
files: [src/lib.rs]
run: cargo test
hints:
  - "`tokenize`: loop over `input.char_indices().peekable()`. Digits and `.` accumulate into a number; `+ - * / ( )` become single tokens; whitespace is skipped; anything else is `Err(ParseError::UnexpectedChar(c, pos))`."
  - "Precedence comes from the call structure: `expr` handles `+`/`-` by calling `term`; `term` handles `*`/`/` by calling `factor`; `factor` handles numbers, parentheses and unary minus."
  - "`expr`: `let mut left = self.term()?; while let Some(Token::Plus | Token::Minus) = self.peek() { let op = self.next(); let right = self.term()?; left = Expr::Binary(Box::new(left), op, Box::new(right)); } Ok(left)`. Looping (not recursing) makes `1 - 2 - 3` left-associative."
  - "`eval`: division by zero is `Err(EvalError::DivisionByZero)`. After parsing the whole expression, leftover tokens are `ParseError::TrailingInput`."
---

Every compiler, query language, config format and calculator starts the same
way: **tokenize** the text, then **parse** the tokens into a tree. Rust's enums
and pattern matching make both pleasant.

## Tokens

A tokenizer (lexer) turns characters into meaningful chunks and drops the rest:

```text
"2 * (3 + 4.5)"  →  Num(2) Star LParen Num(3) Plus Num(4.5) RParen
```

```rust
#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    Num(f64),
    Plus, Minus, Star, Slash,
    LParen, RParen,
}
```

A `Peekable` iterator over `char_indices()` lets the lexer look at the next
character without consuming it, which is what reading a multi-digit number needs.

## A grammar with precedence

Write down what a valid expression is, lowest precedence first:

```text
expr    = term   (("+" | "-") term)*
term    = factor (("*" | "/") factor)*
factor  = NUMBER | "(" expr ")" | "-" factor
```

**Recursive descent** turns each rule into a function. Because `expr` calls
`term`, and `term` calls `factor`, multiplication binds tighter than addition
without any special handling. Parentheses restart at `expr`, so they override it.

The `*` repetition becomes a `while` loop that folds into the left side, which
makes operators **left-associative**: `8 - 3 - 2` is `(8 - 3) - 2`.

## The syntax tree

```rust
pub enum Expr {
    Num(f64),
    Neg(Box<Expr>),
    Binary(Box<Expr>, Token, Box<Expr>),
}
```

Evaluation is then a short recursive `match`. The same tree could just as easily
be printed, optimised, or compiled.

## Errors that help

Report **what** went wrong and **where**: "unexpected character '$' at 4" beats
"parse error". Give each failure its own enum variant, and let `?` carry it up
through the recursive calls.

## Your turn

In `src/lib.rs`, build a calculator for `+ - * /`, parentheses, unary minus and
decimal numbers:

- `tokenize(input) -> Result<Vec<Token>, ParseError>`; an invalid character is
  `UnexpectedChar(char, byte_position)`, a malformed number such as `1.2.3` is
  `InvalidNumber(String)`
- `parse(tokens) -> Result<Expr, ParseError>` with correct precedence and left
  associativity; `UnexpectedEnd` when input stops early, `UnexpectedToken(Token)`
  for a misplaced token, `TrailingInput` if tokens remain
- `eval(&Expr) -> Result<f64, EvalError>`, with `DivisionByZero`
- `calculate(input) -> Result<f64, String>` gluing them together, with errors as
  their `Debug` text
