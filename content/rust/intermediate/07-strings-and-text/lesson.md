---
title: Strings and text
summary: UTF-8 in practice. Bytes versus chars, safe slicing, parsing, building strings efficiently, and Cow for maybe-borrowed text.
order: 7
files: [src/lib.rs]
run: cargo test
hints:
  - "`char_count` is `s.chars().count()`; `truncate_chars(s, n)` finds the byte index with `s.char_indices().nth(n)` and slices up to it (or returns all of `s`)."
  - "`capitalize_words`: split on `' '`, and for each word take `let mut c = word.chars();` then `match c.next() { Some(f) => f.to_uppercase().collect::<String>() + c.as_str(), None => String::new() }`; join with a space."
  - "`parse_rgb(\"#ff8000\")`: `let hex = s.strip_prefix('#')?;`, check `hex.len() == 6 && hex.is_ascii()`, then `u8::from_str_radix(&hex[0..2], 16).ok()?` and so on."
  - "`normalize_spaces(s) -> Cow<str>`: if `!s.contains(\"  \")` return `Cow::Borrowed(s)`; otherwise `Cow::Owned(s.split(' ').filter(|w| !w.is_empty()).collect::<Vec<_>>().join(\" \"))`."
---

Rust strings are always valid **UTF-8**. That guarantee is why some operations
that look simple in other languages are deliberately explicit here.

## Bytes, chars, graphemes

```rust
let s = "héllo";
s.len()               // 6: bytes ('é' is two bytes in UTF-8)
s.chars().count()     // 5: Unicode scalar values
s.bytes()             // an iterator of u8
s.chars()             // an iterator of char
s.char_indices()      // (byte_index, char) pairs
```

A `char` is a Unicode scalar value, not always what a person sees as "one
character": an emoji with a skin-tone modifier is several `char`s. Handling
those (grapheme clusters) needs the `unicode-segmentation` crate.

## Slicing is by byte, and must land on a boundary

```rust
let s = "héllo";
&s[0..1]     // "h"
&s[0..2]     // panics: byte 2 is inside 'é'
```

Find boundaries with `char_indices()`, `find()`, `split_once()` and friends
rather than doing arithmetic on byte offsets. `s.is_char_boundary(i)` checks one.

## Case and ASCII

`to_uppercase()` returns a `String` (German `ß` becomes `SS`: the length can
change). `char::to_uppercase()` returns an **iterator** for the same reason.
For protocols and identifiers that are ASCII by definition, the `_ascii_`
variants (`to_ascii_lowercase`, `eq_ignore_ascii_case`) are faster and exact.

## Parsing

```rust
"42".parse::<i32>()                     // Result<i32, ParseIntError>
u8::from_str_radix("ff", 16)            // Ok(255)
"a,b,,c".split(',')                     // "a", "b", "", "c"
"  x  ".trim()
"key: value".split_once(": ")           // Some(("key", "value"))
line.strip_prefix("GET ")               // Option<&str>
```

`strip_prefix` plus `?` inside a function returning `Option` reads very cleanly.

## Building strings

```rust
let mut out = String::with_capacity(64);
out.push_str("total: ");
out.push('=');
use std::fmt::Write;                     // enables write! into a String
write!(out, "{:>8.2}", 3.14159).unwrap();
let joined = parts.join(", ");
```

## Cow: borrow when you can, own when you must

A function that usually returns its input unchanged but sometimes has to build
a new string can avoid allocating in the common case:

```rust
use std::borrow::Cow;

fn escape(s: &str) -> Cow<str> {
    if s.contains('<') {
        Cow::Owned(s.replace('<', "&lt;"))
    } else {
        Cow::Borrowed(s)
    }
}
```

`Cow<str>` derefs to `&str`, so callers mostly do not care which one they got.

## Your turn

In `src/lib.rs`:

- `char_count(s)`: characters, not bytes
- `truncate_chars(s, n)`: the first `n` characters as a slice of `s`, never
  splitting a character
- `capitalize_words(s)`: upper-case the first character of each space-separated
  word: `"élan vital"` gives `"Élan Vital"`
- `parse_rgb(s)`: `"#ff8000"` gives `Some((255, 128, 0))`; anything malformed
  (missing `#`, wrong length, non-hex, non-ASCII) gives `None`
- `normalize_spaces(s)`: collapse runs of spaces into one space, returning
  `Cow::Borrowed` when there is nothing to change
