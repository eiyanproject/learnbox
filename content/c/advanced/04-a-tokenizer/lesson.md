---
title: "Capstone: a tokenizer"
summary: Turning text into tokens the way every parser starts - a cursor, a switch, and no allocation per token.
order: 4
files: [lex.c, lex.h]
run: gcc -std=c17 -Wall lex.c -o lex && ./lex
hints:
  - "Keep a cursor into the input. Skip whitespace, look at the current character, and decide what kind of token starts there."
  - "A token points INTO the input with a length rather than owning a copy - no allocation, and the caller keeps the input alive."
  - "Numbers: consume digits while isdigit. Identifiers: a letter or underscore, then letters, digits or underscores."
  - "`lex_next` returns a token with kind TOK_END at the end of the input, and TOK_ERROR for a character it does not recognise."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **parser** | reads structured text into a model |
| **tokenizer** / **lexer** | turns a flat string into tokens |
| **token** | one meaningful piece: a number, a name, a `+` |
| **identifier** | a name: letters, digits and `_`, not starting with a digit |
| **borrow** | point into the input instead of copying; the input must outlive the tokens |
| **whitespace** | spaces, tabs and newlines |
| **peek** | look at the next character without consuming it |
| **first refusal** | checking longer tokens first, such as `==` before `=` |
| **contract** | the documented rules a function's caller must follow |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall lex.c -o lex && ./lex` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `enum TokenKind { TOK_END, ... };` | named integer constants for the kinds |
| `const char *start; int length;` | where a token is in the input |
| `long value` | a number token's value |
| `<ctype.h>` | `isdigit`, `isalpha`, `isspace` |
| `isdigit((unsigned char)c)` | the cast avoids undefined behaviour for bytes above 127 |
| `switch (c) { case '+': ... }` | single-character tokens |

---

Every parser, compiler and config reader starts the same way: turn a flat
string into a sequence of **tokens**. It is the smallest real program that uses
everything in this track.

## The shape

```c
enum TokenKind { TOK_END, TOK_NUMBER, TOK_IDENT, TOK_PLUS, ..., TOK_ERROR };

struct Token {
    enum TokenKind kind;
    const char *start;   /* points INTO the input */
    int length;
    long value;          /* for numbers */
};
```

A token **borrows** rather than owns. No allocation per token, no freeing, and
the whole lexer needs no memory management at all — at the cost of a rule the
caller must honour: *the input must outlive the tokens*. Write that down,
because C cannot say it.

This is exactly how real lexers work, and it is why they are fast.

## The loop

```c
skip_whitespace(lex);
if (at_end) return token(TOK_END);
char c = peek(lex);
if (isdigit(c)) return number(lex);
if (isalpha(c) || c == '_') return identifier(lex);
switch (c) { case '+': ... }
return token(TOK_ERROR);
```

Order matters: digits before identifiers, or `123` starts looking like a name.
And the single-character cases come last so the multi-character ones get first
refusal — the same reason `==` must be checked before `=`.

## ctype and the char trap

```c
isdigit((unsigned char)c)
```

The `<ctype.h>` functions take an `int` whose value must be representable as
`unsigned char` **or** be `EOF`. A plain `char` is signed on x86, so a byte
above 127 becomes negative and the call is undefined. The cast is not
pedantry — it is the documented contract, and this is a real bug in a lot of
code.

## Your turn

In `lex.h` and `lex.c`:

- `enum TokenKind`: `TOK_END`, `TOK_NUMBER`, `TOK_IDENT`, `TOK_PLUS`,
  `TOK_MINUS`, `TOK_STAR`, `TOK_SLASH`, `TOK_LPAREN`, `TOK_RPAREN`,
  `TOK_ERROR`
- `struct Token` and `struct Lexer`
- `void lex_init(struct Lexer *lex, const char *input)`
- `struct Token lex_next(struct Lexer *lex)`
- `int lex_count(const char *input)` — how many tokens before `TOK_END`,
  or -1 if any is `TOK_ERROR`
