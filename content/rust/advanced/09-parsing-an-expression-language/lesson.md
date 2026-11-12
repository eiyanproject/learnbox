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

Every compiler, query language, configuration format and calculator starts
the same way. The input is a string of characters, and before the
program can do anything with `2 * (3 + 4.5)`, it has to work out what that
string *means*: that `4.5` is one number, that the addition happens first
because of the brackets, and that the multiplication then uses its result.
That happens in two steps:

1. **Tokenizing** (also called lexing): cut the characters into meaningful
   pieces, **tokens**, such as numbers and operators, dropping spaces.
2. **Parsing**: arrange the tokens into a **syntax tree** that shows which
   operation applies to which operands.

Once you have the tree, evaluating it, printing it or compiling it is a short
recursive `match`. This lesson builds a calculator this way, and Rust's enums,
pattern matching, `Box` and `?` turn out to fit the job closely.

## Tokens

A tokenizer reads characters and produces tokens:

```text
"2 * (3 + 4.5)"  →  Num(2) Star LParen Num(3) Plus Num(4.5) RParen
```

The kinds of token are a natural enum, with the number variant carrying its
value:

```rust
#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    Num(f64),
    Plus, Minus, Star, Slash,
    LParen, RParen,
}
```

Most tokens are one character, decided by looking at that character alone.
A number is the exception: `4.5` is three characters, and the tokenizer only
knows the number has ended when it sees the next character is not a digit or
`.`. It needs to **look at** that next character without **using it up**,
since the character after a number (`)` here) is the start of the next
token.

`Peekable` gives an iterator exactly that ability. `.peekable()` wraps any
iterator, adding `peek()`, which returns a reference to the next item
without consuming it:

```rust
let mut chars = "42+".char_indices().peekable();
chars.peek()      // Some(&(0, '4')): looked at, still there
chars.next()      // Some((0, '4')):  now consumed
```

(A fragment.) `char_indices()` yields each character with its **byte
position**, which is what an error message needs to say *where* the problem
is. To read a number: take characters while `peek()` shows a digit or `.`,
collecting them into a `String`, then `parse::<f64>()` it. Text like `1.2.3`
collects fine but does not parse, which is the `InvalidNumber` error.

## A grammar with precedence

The parser needs rules for what a valid expression is. Written down in a
compact notation, a **grammar**, with the lowest-precedence operators first:

```text
expr    = term   (("+" | "-") term)*
term    = factor (("*" | "/") factor)*
factor  = NUMBER | "(" expr ")" | "-" factor
```

Read `=` as "is", `|` as "or", quotes as literal tokens, and `( ... )*` as
"zero or more times". So: an *expr* is a *term*, followed by any number of
`+` or `-` and further terms. A *term* is the same with `*` and `/` over
*factors*. A *factor* is a number, a bracketed expression, or a minus sign in
front of another factor.

**Recursive descent** turns each rule into one function, which calls the
functions for the rules it mentions. Precedence then comes for free, from the
call structure. `expr` cannot see a `*` at all; it hands everything between
`+` signs to `term`, which collects the multiplications first. For
`1 + 2 * 3`:

```text
expr
├── term ──> factor ──> 1          (term sees no * after 1, returns 1)
├── sees +
└── term
    ├── factor ──> 2
    ├── sees *
    └── factor ──> 3               (term returns 2 * 3)
result: 1 + (2 * 3)
```

Brackets work because `factor` calls `expr` again for what is inside them,
starting over from the lowest precedence, so `(1 + 2) * 3` groups the
addition first.

### Left associativity: loop, do not recurse

`8 - 3 - 2` must mean `(8 - 3) - 2`, which is 3, not `8 - (3 - 2)`, which is
7: operators of equal precedence group from the **left**. The `( ... )*`
repetition becomes a `while` loop that keeps folding into the left-hand
side:

```text
left = 8
see -, right = 3:  left = (8 - 3)
see -, right = 2:  left = ((8 - 3) - 2)
no more - or +:    return left
```

Writing it instead as `expr = term "-" expr`, with the function calling
itself for the right-hand side, would build `8 - (3 - 2)`, the wrong tree.
The exercise's tests check the tree shape for `1 - 2 - 3`.

## The syntax tree

The tree is another enum. An operation holds its operands, which are
themselves trees, so the enum is recursive and needs `Box` (Intermediate
lesson 5):

```rust
pub enum Expr {
    Num(f64),
    Neg(Box<Expr>),
    Binary(Box<Expr>, Token, Box<Expr>),
}
```

`Binary` stores the operator as its `Token` (`Plus`, `Star`, ...) between
the two operands. Evaluating it is a recursive `match`: a `Num` is its value,
a `Neg` is minus the value of its operand, and a `Binary` evaluates both
sides, then applies the operator. The same tree could just as well be
printed, simplified, or turned into machine code; that separation is why
compilers are built this way.

## Errors that help

A parser's errors are read by people who just typed something wrong, so they
should say **what** went wrong and **where**: "unexpected character '$' at
4" beats "parse error". Give each kind of failure its own enum variant,
carrying the details, and let `?` pass it up through the recursive calls:
the moment `factor` finds a problem three calls deep, `?` returns it through
`term` and `expr` to the caller.

The exercise's parser distinguishes:

| Variant | When | Example |
|---|---|---|
| `UnexpectedChar(c, pos)` | the tokenizer meets a character no token starts with | `"1 + $"`: `('$', 4)` |
| `InvalidNumber(text)` | digits and dots that do not form a number | `"1.2.3"` |
| `UnexpectedEnd` | the tokens run out where something was needed | `"1 +"`, `"(1 + 2"`, no tokens |
| `UnexpectedToken(tok)` | a token where a factor should start | `"* 2"`: `Star` |
| `TrailingInput` | a complete expression, with tokens left over | `"1 2"`, `"(1))"` |

`TrailingInput` is checked once, after the top-level `expr` returns: if any
tokens remain, they were not part of the expression.

## Run it

A smaller version of the same idea, for whole numbers with only `+` and
`*`, and no brackets or errors: two grammar rules, so two functions, plus a
tokenizer.

```rust
#[derive(Debug, Clone, Copy, PartialEq)]
enum Tok {
    Num(i64),
    Plus,
    Star,
}

#[derive(Debug)]
enum Expr {
    Num(i64),
    Add(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
}

fn tokenize(input: &str) -> Vec<Tok> {
    let mut out = Vec::new();
    let mut chars = input.chars().peekable();
    while let Some(&c) = chars.peek() {
        if c.is_ascii_digit() {
            let mut n = 0;
            while let Some(&d) = chars.peek() {
                let Some(digit) = d.to_digit(10) else { break };
                n = n * 10 + digit as i64;
                chars.next();
            }
            out.push(Tok::Num(n));
        } else {
            chars.next();
            match c {
                '+' => out.push(Tok::Plus),
                '*' => out.push(Tok::Star),
                _ => {}                         // skip spaces (and, here, anything else)
            }
        }
    }
    out
}

struct Parser {
    tokens: Vec<Tok>,
    pos: usize,
}

impl Parser {
    fn peek(&self) -> Option<Tok> {
        self.tokens.get(self.pos).copied()
    }

    // sum = product ("+" product)*
    fn sum(&mut self) -> Expr {
        let mut left = self.product();
        while self.peek() == Some(Tok::Plus) {
            self.pos += 1;
            let right = self.product();
            left = Expr::Add(Box::new(left), Box::new(right));
        }
        left
    }

    // product = NUMBER ("*" NUMBER)*
    fn product(&mut self) -> Expr {
        let mut left = self.number();
        while self.peek() == Some(Tok::Star) {
            self.pos += 1;
            let right = self.number();
            left = Expr::Mul(Box::new(left), Box::new(right));
        }
        left
    }

    fn number(&mut self) -> Expr {
        let Some(Tok::Num(n)) = self.peek() else { panic!("expected a number") };
        self.pos += 1;
        Expr::Num(n)
    }
}

fn eval(e: &Expr) -> i64 {
    match e {
        Expr::Num(n) => *n,
        Expr::Add(a, b) => eval(a) + eval(b),
        Expr::Mul(a, b) => eval(a) * eval(b),
    }
}

fn main() {
    let tokens = tokenize("1 + 2 * 3");
    println!("{tokens:?}");
    let tree = Parser { tokens, pos: 0 }.sum();
    println!("{tree:?}");
    println!("{}", eval(&tree));
    for text in ["2 * 3 + 4 * 5", "10 + 20 + 30"] {
        let tree = Parser { tokens: tokenize(text), pos: 0 }.sum();
        println!("{text} = {}", eval(&tree));
    }
}
```

```output
[Num(1), Plus, Num(2), Star, Num(3)]
Add(Num(1), Mul(Num(2), Num(3)))
7
2 * 3 + 4 * 5 = 26
10 + 20 + 30 = 60
```

The printed tree shows the precedence: the `Mul` sits inside the `Add`, so
it is evaluated first. The parser keeps a position `pos` into the token list,
and `peek` looks at the token there without moving on. `number` panics on a
missing number; the exercise turns each such place into a `ParseError`
returned with `Err`, which `?` passes up.

## Your turn

In `src/lib.rs`, build a calculator for `+ - * /`, brackets, unary minus and
decimal numbers, using the types in the starter:

- `tokenize(input) -> Result<Vec<Token>, ParseError>`:
  - numbers are digits and dots (`2`, `4.5`), parsed as `f64`; something like
    `1.2.3` is `InvalidNumber("1.2.3")`, with the text as written
  - `+ - * / ( )` are one token each; whitespace is skipped; input with only
    whitespace gives an empty list
  - any other character is `UnexpectedChar(c, position)`, the position being
    the character's **byte** index: `"1 + $"` gives `('$', 4)`
- `parse(tokens) -> Result<Expr, ParseError>`, following the three-rule
  grammar above:
  - correct precedence (`1 + 2 * 3` is 7) and left associativity:
    `1 - 2 - 3` must produce `Binary(Binary(1, Minus, 2), Minus, 3)`
  - unary minus can repeat: `--4` is `Neg(Neg(4))`, which is 4
  - the errors from the table above: `UnexpectedEnd` when the tokens run out
    (including an empty list and a missing `)`), `UnexpectedToken(t)` for a
    token that cannot start a factor, `TrailingInput` when tokens remain after
    a complete expression
- `eval(&Expr) -> Result<f64, EvalError>`: dividing by exactly zero is
  `Err(DivisionByZero)`, so check the divisor before dividing (floats would
  otherwise give infinity)
- `calculate(input)` is given: it chains the three, turning any error into
  its `Debug` text, such as `"DivisionByZero"` or `"UnexpectedChar('#', 4)"`

A `Parser` struct holding the tokens and a position, with methods `expr`,
`term`, `factor`, `peek` and `next`, keeps this tidy, as in the program
above.
