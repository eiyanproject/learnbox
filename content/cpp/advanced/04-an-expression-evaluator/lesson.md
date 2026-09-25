---
title: An expression evaluator
summary: The capstone - a tokenizer, a recursive-descent parser building a variant tree of unique_ptrs, and std::visit to evaluate it.
order: 4
files: [eval.h]
run: g++ -std=c++20 -Wall -fsyntax-only eval.h && echo "header compiles"
hints:
  - "Tokenize first: numbers, the five operators, parentheses. Anything else is a ParseError."
  - "The grammar is three functions. expr handles + and -, term handles * and /, factor handles a number, a unary minus, or a parenthesised expr. Precedence falls out of which function calls which."
  - "A variant cannot contain itself, so Binary holds `std::unique_ptr<Node>` and Node holds the variant. That indirection is what makes the recursion legal."
  - "`evaluate` catches ParseError and returns std::nullopt - the caller asked whether the text is a valid expression, which is not exceptional."
---

Everything so far, in one program: `"2 + 3 * (4 - 1)"` to `11`.

## The three stages

```
text  ->  tokens  ->  tree  ->  value
```

Each stage is separately testable, which is the reason to have three of them
rather than one clever loop.

## Tokenizing

Walk the string; emit a token per number, operator and parenthesis; skip
whitespace; reject anything else. The tokenizer knows nothing about grammar —
`) ) ) + *` tokenizes fine and fails later.

## The grammar

```
expr   := term (('+' | '-') term)*
term   := factor (('*' | '/') factor)*
factor := '-' factor | number | '(' expr ')'
```

One function per rule, each calling the next. **Precedence is the nesting**:
`expr` cannot see individual numbers, only whole `term`s, so `2 + 3 * 4` parses
as `2 + (3 * 4)` without a precedence table anywhere. Left associativity comes
from the loop — `8 - 3 - 2` folds left into `(8 - 3) - 2`.

Recursive descent is this and nothing more. It is how a surprising number of
real parsers are written, for the reason that you can read it.

## The tree

```cpp
struct Num    { double value; };
struct Binary { char op; std::unique_ptr<Node> lhs, rhs; };
struct Node   { std::variant<Num, Binary> value; };
```

A `std::variant` holds exactly one of its alternatives and knows which. It
cannot contain itself — its size would be undefined — so `Binary` stores
`unique_ptr<Node>`, and the pointer breaks the cycle. The nodes own their
children, so destroying the root destroys the tree.

## std::visit

```cpp
return std::visit(overloaded{
    [](const Num& n)    { return n.value; },
    [](const Binary& b) { return apply(b.op, eval(*b.lhs), eval(*b.rhs)); },
}, node.value);
```

`std::visit` calls the branch matching what the variant currently holds, and
**fails to compile if any alternative is unhandled** — the exhaustiveness a
`switch` on an enum will not give you.

`overloaded` is the small idiom that makes a set of lambdas into one callable:

```cpp
template <typename... Ts> struct overloaded : Ts... { using Ts::operator()...; };
```

## Your turn

In `eval.h`:

- `struct ParseError : std::runtime_error`
- `std::vector<Token> tokenize(std::string_view text)`
- `std::unique_ptr<Node> parse(std::string_view text)`
- `double eval(const Node& node)`
- `std::optional<double> evaluate(std::string_view text)`
