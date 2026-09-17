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

Macros write code for you at compile time. `println!`, `vec!`, `assert_eq!`
and `format!` are all macros. **Declarative macros** (`macro_rules!`) match on
the *syntax* you pass them and expand into new syntax.

## The shape of a macro

```rust
#[macro_export]
macro_rules! square {
    ($x:expr) => {
        $x * $x
    };
}

square!(3 + 1)       // expands to (3 + 1) * (3 + 1): expression fragments keep their grouping
```

Each rule is `(matcher) => { transcriber };`. The first rule that matches wins.
`#[macro_export]` makes the macro available to users of the crate as `crate_name::square!`.

## Fragment specifiers

| Specifier | Matches |
|---|---|
| `expr` | an expression: `1 + 2`, `foo()`, `x` |
| `ident` | an identifier: `count`, `MyType` |
| `ty` | a type: `u32`, `Vec<String>` |
| `pat` | a pattern |
| `literal` | a literal: `42`, `"hi"` |
| `tt` | a single token tree: anything, as one token or one `(...)`/`[...]`/`{...}` group |
| `block`, `stmt`, `path`, `lifetime`, `vis`, `item` | what they say |

## Repetition

`$( ... ),*` matches zero or more comma-separated repetitions; `+` means one or
more; `?` zero or one. The same `$( ... )*` in the transcriber repeats the
output once per match:

```rust
macro_rules! my_vec {
    ($($item:expr),* $(,)?) => {{            // $(,)? allows a trailing comma
        let mut v = Vec::new();
        $( v.push($item); )*
        v
    }};
}
```

The double braces `{{ ... }}` produce a **block expression**, so the macro can
declare local variables and still be used where an expression is expected.

## Recursion

A macro can call itself on the rest of its input, which is how you process
lists one item at a time:

```rust
macro_rules! sum {
    ($x:expr) => { $x };
    ($x:expr, $($rest:expr),+) => { $x + sum!($($rest),+) };
}
```

## Hygiene

Variables declared inside a macro do not clash with variables at the call
site: the `v` inside `my_vec!` is a different `v` from one the caller has. Use
absolute paths like `::std::collections::HashMap` inside exported macros, so they
work regardless of what the caller has imported.

## Macro or function?

Prefer functions. Reach for a macro when a function cannot do it: a variable
number of arguments of different types, generating items (structs, impls),
or new syntax such as `key => value`.

## Your turn

In `src/lib.rs`, all exported with `#[macro_export]`:

- `hashmap!{ "a" => 1, "b" => 2 }` builds a `HashMap`, allowing a trailing comma
  and an empty invocation (give the empty case a type at the call site)
- `max_of!(a, b, c, ...)`: the largest of one or more expressions, recursively,
  evaluating each argument exactly once
- `count!(tokens...)`: the number of token trees given, as a `usize` constant
- `newtype!(Name, InnerType)`: defines `pub struct Name(pub InnerType)` deriving
  `Debug, Clone, Copy, PartialEq`, plus `From<InnerType>`
