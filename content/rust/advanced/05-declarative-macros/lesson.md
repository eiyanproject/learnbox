---
title: Declarative macros
summary: macro_rules! from first principles. Matchers, fragment types, repetition, recursion, and hygiene.
order: 5
files: [src/lib.rs]
run: cargo test
hints:
  - "`hashmap!`: `($($key:expr => $value:expr),* $(,)?) => {{ let mut map = ::std::collections::HashMap::new(); $( map.insert($key, $value); )* map }}`."
  - "`max_of!`: a single-expression arm `($x:expr) => { $x };` and a recursive arm `($x:expr, $($rest:expr),+) => {{ let a = $x; let b = max_of!($($rest),+); if a > b { a } else { b } }};`."
  - "`count!`: `() => { 0usize };` and `($head:tt $($tail:tt)*) => { 1usize + count!($($tail)*) };`."
  - "`newtype!`: `($name:ident, $inner:ty) => { #[derive(Debug, Clone, Copy, PartialEq)] pub struct $name(pub $inner); impl From<$inner> for $name { fn from(v: $inner) -> Self { $name(v) } } };`. Export macros with `#[macro_export]`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **macro** | code that writes code, at compile time; called with `!` |
| **expansion** | replacing a macro call with the code it produces, before type-checking |
| **declarative macro** | one written with `macro_rules!`, matching syntax against patterns |
| **procedural macro** | a Rust program running inside the compiler, such as `derive` |
| **rule** | `(matcher) => { transcriber };`; tried top to bottom |
| **matcher** | the pattern for the tokens in the call |
| **transcriber** | the code produced, with metavariables substituted |
| **metavariable** | a name for a matched piece: `$x` |
| **fragment specifier** | what kind of piece: `expr`, `ident`, `ty`, `tt`, `pat`, `literal`, `block` |
| **token tree** (`tt`) | one token, or one bracketed group counted as one |
| **grouping** | an `expr` keeps its own brackets; pasted `tt`s do not |
| **repetition** | `$( ... ),*` zero or more, `,+` one or more, `?` zero or one |
| **trailing comma** | allowed with `$(,)?` |
| **block expression** | the inner `{ }` of `{{ ... }}`, so the macro can declare locals and still give a value |
| **recursive macro** | one that calls itself on the rest of its input, ending at a base case |
| **evaluate once** | bind each argument to a local first, so side effects happen once |
| **hygiene** | variables a macro declares cannot clash with the caller's |
| **full path** | `::std::collections::HashMap`, which works whatever the caller imported |
| **newtype** | a one-field tuple struct wrapping another type |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests, which import your macros by name |

### Rust names

| Name | What it does |
|---|---|
| `macro_rules! square { ($x:expr) => { $x * $x }; }` | a one-rule macro |
| `#[macro_export]` | makes the macro usable from other crates |
| `($($k:expr => $v:expr),* $(,)?) => {{ ... }}` | the `hashmap!` matcher |
| `let mut map = ::std::collections::HashMap::new(); $( map.insert($k, $v); )* map` | its transcriber |
| `($x:expr) => ...; ($x:expr, $($rest:expr),+) => ...` | base and recursive rules |
| `{{ let a = $a; let b = max_of!($($rest),+); if a > b { a } else { b } }}` | evaluate each argument once |
| `() => { 0usize }; ($head:tt $($tail:tt)*) => { 1usize + count!($($tail)*) }` | counting token trees |
| `($name:ident, $inner:ty) => { pub struct $name(pub $inner); ... }` | generating items |

### Errors

| Error | Means |
|---|---|
| `error: no rules expected ;` | the call did not fit any rule; the token named broke the match |
| `unexpected end of macro invocation` | the call stopped before a rule was satisfied |
| `failed to resolve: use of undeclared type HashMap` | a macro using a short path the caller has not imported |

---

Some code cannot be written as a function. `println!("{} {}", a, b)` takes
any number of arguments of any types, and checks the format string against
them while compiling. `vec![1, 2, 3]` builds a vector from a list of any
length. `#[derive(Debug)]` writes a whole `impl` for you. A function has a
fixed number of typed parameters and runs while the program runs, so none of
these could be functions.

They are **macros**: code that writes code, at compile time. A macro call
(the `!` marks one) is replaced, before the program is type-checked, by the
code the macro produces; this is called **expansion**. This lesson covers
**declarative macros**, written with `macro_rules!`, which work by matching
the *syntax* you give them against patterns and producing new syntax. (The
other kind, procedural macros, such as `derive`, are Rust programs that run
inside the compiler, and are a topic for a separate crate.)

## The shape of a macro

```rust
#[macro_export]
macro_rules! square {
    ($x:expr) => {
        $x * $x
    };
}

square!(3 + 1)       // expands to (3 + 1) * (3 + 1)
```

(A fragment.) A macro is a list of **rules**, each written
`(matcher) => { transcriber };`:

- The **matcher** `($x:expr)` is a pattern for the tokens inside the call's
  brackets. `$x` is a **metavariable**, a name for a matched piece, and
  `:expr` says what kind of piece it must be: here, one expression.
- The **transcriber** `{ $x * $x }` is the code to produce, with each
  metavariable replaced by what it matched.
- Rules are tried from top to bottom, and the first matcher that fits wins.
  If none fits, the call is a compile error.

Calls may use any bracket: `square!(3)`, `square![3]` and `square!{3}` are
the same macro. By convention `vec![...]` uses square brackets and
`hashmap!{...}`-style macros braces, because they look like the literal they
build.

`#[macro_export]` makes the macro usable by other crates, as
`crate_name::square!`, or after `use crate_name::square;`. Without it, a
`macro_rules!` macro can only be used further down in the same crate.

There is no "macro step" you can look at by default, but you can reason about
expansion by hand: replace the call with the transcriber, substituting the
matched pieces.

## Fragment specifiers

The `:expr` part is a **fragment specifier**. The common ones:

| Specifier | Matches | Example |
|---|---|---|
| `expr` | an expression | `1 + 2`, `foo()`, `x` |
| `ident` | an identifier, a name | `count`, `MyType` |
| `ty` | a type | `u32`, `Vec<String>` |
| `pat` | a pattern | `Some(x)`, `1..=5` |
| `literal` | a literal | `42`, `"hi"` |
| `tt` | one **token tree**: a single token, or a whole `( )`, `[ ]` or `{ }` group | `+`, `x`, `(a b c)` |
| `block`, `stmt`, `path`, `lifetime`, `vis`, `item` | what their names say | |

The specifier matters for more than matching. A piece matched as `expr` is
handed on as **one expression**, which keeps its grouping. A piece matched
as a sequence of `tt` tokens is pasted in token by token, which does not:

```rust
macro_rules! square_text {
    ($x:expr) => { $x * $x };
}
macro_rules! double_tt {
    ($($t:tt)*) => { $($t)* * 2 };
}
fn main() {
    println!("{} {}", square_text!(3 + 1), double_tt!(3 + 1));
}
```

```output
16 5
```

`square_text!(3 + 1)` is `(3 + 1) * (3 + 1)`, 16, as you would hope.
`double_tt!(3 + 1)` pasted the tokens `3 + 1 * 2`, and since `*` binds
tighter than `+`, that is 5. (In C, where macros paste text, `square` has
exactly this bug, and C programmers wrap every argument in parentheses by
habit.) Prefer `expr` for expressions.

A matcher can also contain plain tokens, which must appear literally in the
call: `($key:expr => $value:expr)` expects an expression, then `=>`, then
another. If the call does not fit any rule, the error says which token
broke the match:

```text
error: no rules expected `;`
 --> src/main.rs:6:26
  |
1 | macro_rules! sum {
  | ---------------- when calling this macro
...
6 |     println!("{}", sum!(1; 2));
  |                          ^ no rules expected this token in macro call
```

## Repetition

`$( ... )` with a **repetition operator** after it matches the inside any
number of times:

- `$( ... ),*`: zero or more times, separated by commas (the `,` before the
  `*` is the separator; any token works);
- `$( ... ),+`: one or more times;
- `$( ... )?`: zero or one time.

In the transcriber, the same `$( ... )*` repeats its contents once per
match, so each metavariable inside must have been matched inside a
repetition too:

```rust
macro_rules! my_vec {
    ($($item:expr),* $(,)?) => {{
        let mut v = Vec::new();
        $( v.push($item); )*
        v
    }};
}
```

Step by step, for `my_vec![1, 2, 3,]`:

1. `$($item:expr),*` matches `1`, `2`, `3`, so `$item` holds three
   expressions.
2. `$(,)?` matches the trailing comma (and would match nothing if there were
   none). It is the usual way to allow one.
3. The transcriber repeats `v.push($item);` three times:

```rust
{
    let mut v = Vec::new();
    v.push(1);
    v.push(2);
    v.push(3);
    v
}
```

The **double braces** `{{ ... }}` matter. The outer pair belongs to the rule
syntax; the inner pair is part of the output, making it a **block
expression**: a block whose value is its last expression, `v`. That lets the
macro declare local variables and still be used where one value is
expected, as in `let made = my_vec![1, 2, 3];`.

## Recursion

A macro can call itself, usually on the rest of its input, to process a list
one item at a time:

```rust
macro_rules! sum {
    ($x:expr) => { $x };
    ($x:expr, $($rest:expr),+) => { $x + sum!($($rest),+) };
}
```

(A fragment.) The first rule is the **base case**, one expression. The
second takes the first expression and the remaining one-or-more, and calls
`sum!` on the remainder. `sum!(1, 2, 3)` expands as:

```text
sum!(1, 2, 3)
  1 + sum!(2, 3)
  1 + (2 + sum!(3))
  1 + (2 + 3)
```

Order of rules matters: `sum!(3)` would not fit the second rule (it needs at
least two), so it reaches the base case.

### Evaluate each argument once

A macro that writes `$a` twice in its output **evaluates** `$a` twice, since
the expression is pasted in two places. With an argument that has side
effects, that is a bug a function could never have:

```rust
macro_rules! bigger {
    ($a:expr, $b:expr) => { if $a > $b { $a } else { $b } };
}

fn next(v: i32, calls: &mut i32) -> i32 {
    *calls += 1;
    v
}

fn main() {
    let mut calls = 0;
    let m = bigger!(next(1, &mut calls), next(5, &mut calls));
    println!("{m} after {calls} calls");
}
```

```output
5 after 3 calls
```

Two arguments, three calls: `next(5, ...)` ran once in the comparison and
again as the result. The fix is to evaluate each argument into a local
variable first, inside a block: `{{ let a = $a; let b = $b; if a > b { a }
else { b } }}`. The exercise's `max_of!` is tested for exactly this.

## Hygiene

Variables a macro declares do not clash with the caller's variables of the
same name:

```rust
macro_rules! make_v {
    () => { let v = 99; };
}

let v = 5;
make_v!();
println!("{v}");      // 5: the macro's v is a different variable
```

(A fragment.) Each name keeps track of where it was written, the macro
definition or the call site, and two names only refer to the same variable
if both were written in the same place. This is called **hygiene**. It is
why `my_vec!`'s internal `v`, or the exercise's internal `map`, cannot
collide with a caller's `map`, which the tests check.

Hygiene covers local variables, not paths to items. A macro that writes
`HashMap::new()` depends on the **caller** having `use
std::collections::HashMap;`. Exported macros therefore use full paths
starting with `::`, such as `::std::collections::HashMap::new()`, which work
whatever the caller has imported.

## Macro or function?

Prefer a function: it has typed parameters, clear error messages, and
evaluates each argument once by construction. Reach for a macro only when a
function cannot do the job:

- a variable number of arguments, possibly of different types (`println!`);
- new syntax, such as `key => value` pairs;
- generating **items**: structs, impls, functions (`newtype!` in the
  exercise defines a whole struct);
- work that must happen at compile time, such as `count!` producing a
  constant.

## Run it

```rust
macro_rules! square {
    ($x:expr) => {
        $x * $x
    };
}

macro_rules! my_vec {
    ($($item:expr),* $(,)?) => {{
        let mut v = Vec::new();
        $( v.push($item); )*
        v
    }};
}

macro_rules! sum {
    ($x:expr) => { $x };
    ($x:expr, $($rest:expr),+) => { $x + sum!($($rest),+) };
}

fn main() {
    println!("{}", square!(3 + 1));          // (3 + 1) * (3 + 1), not 3 + 1 * 3 + 1
    let v = 5;
    let made: Vec<i32> = my_vec![1, 2, 3,];  // trailing comma accepted
    println!("{made:?} {v}");                // the macro's own v left this one alone
    println!("{}", sum!(1, 2, 3, 4));
}
```

```output
16
[1, 2, 3] 5
10
```

## Your turn

In `src/lib.rs`, each macro with `#[macro_export]` (the tests import them by
name from your crate):

- `hashmap!{ "a" => 1, "b" => 2 }` builds a `HashMap` of the pairs. It must
  accept a trailing comma (`hashmap!{ 1 => "one", }`) and no pairs at all
  (`hashmap!{}`, where the caller gives the type). The starter has the empty
  rule; one rule with `$( ... ),* $(,)?` can replace it and cover all three.
  Use the full path `::std::collections::HashMap`, and keep the internal
  variable hygienic: the tests pass a caller variable named `map` as a value.
- `max_of!(a, b, c, ...)`: the largest of one or more expressions, with a
  base rule and a recursive rule. It works for anything comparable with `>`
  (numbers, `&str`), and evaluates **each argument exactly once**: the tests
  count calls.
- `count!(tokens...)`: how many token trees it was given, as a `usize` that
  can be used in a `const`: `count!(a b c d)` is 4, `count!()` is 0, and
  `count!((nested group) [counts] {as one})` is 3, since each bracketed group
  is one token tree. Recursion with `tt` does it: one plus the count of the
  rest.
- `newtype!(Name, InnerType)`: defines `pub struct Name(pub InnerType);`
  deriving `Debug, Clone, Copy, PartialEq`, plus `impl From<InnerType> for
  Name`. Use `ident` for the name and `ty` for the type.
