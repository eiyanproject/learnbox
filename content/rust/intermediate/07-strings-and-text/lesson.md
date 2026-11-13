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
  - "`normalize_spaces(s) -> Cow<str>`: if `s` has no `\"  \"` and does not start or end with `' '`, return `Cow::Borrowed(s)`; otherwise `Cow::Owned(s.split(' ').filter(|w| !w.is_empty()).collect::<Vec<_>>().join(\" \"))`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **Unicode** | gives every character in every writing system a number |
| **code point** | that number: `h` is 104, `é` is 233 |
| **UTF-8** | stores code points as 1 to 4 bytes each; Rust strings are always valid UTF-8 |
| **ASCII** | the first 128 code points (English letters, digits, punctuation), one byte each |
| **byte length** | `len()`: what is stored, and what slicing uses |
| **`char`** | one Unicode scalar value (a code point), 4 bytes in memory |
| **grapheme cluster** | what a reader sees as one character, possibly several `char`s |
| **char boundary** | a byte position between characters; slices must start and end on one |
| **case mapping** | upper or lower case; can change length (`ß` becomes `SS`) |
| **hexadecimal** (hex) | base 16, digits 0-9 and a-f |
| **radix** | the base of a number system |
| **capacity** | room reserved in a `String`'s buffer |
| **`Cow`** (clone on write) | either a borrowed `&str` or an owned `String`; copies only when a change is needed |
| **`'_`** | an elided lifetime: "the obvious one", here tied to the input |
| **collapse spaces** | turn each run of spaces into one |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests, which use accented and Japanese text |

### Rust names

| Name | What it does |
|---|---|
| `s.len()`, `s.chars().count()` | length in bytes; in characters |
| `s.char_indices()` | each character with its byte index |
| `s.char_indices().nth(n)` | where character `n` starts, or `None` |
| `s.is_char_boundary(i)` | is byte `i` between characters |
| `s.to_uppercase()`, `c.to_uppercase()` | a new `String`; an iterator of `char`s |
| `to_ascii_lowercase`, `eq_ignore_ascii_case`, `is_ascii_digit`, `s.is_ascii()` | ASCII-only versions |
| `s.split(',')`, `s.split_once('=')`, `s.strip_prefix('#')` | keep empty pieces; split once; remove a prefix (`Option`) |
| `u8::from_str_radix("ff", 16)` | parse hex text |
| `String::with_capacity(64)`, `s.push(c)`, `s.push_str(t)` | build text in one buffer |
| `use std::fmt::Write; write!(s, "{:>8.2}", x).unwrap();` | append formatted text |
| `parts.join(" ")` | joins with a separator |
| `Cow::Borrowed(s)`, `Cow::Owned(t)`, `.into_owned()` | the two variants; get a `String` |

### Errors

| Error | Means |
|---|---|
| `end byte index 2 is not a char boundary; it is inside 'é'` | a panic from slicing inside a character |
| `ParseIntError` | `from_str_radix` given a non-hex character |

---

Text is where many programs meet the real world: names with accents, files
in other languages, emoji in chat messages. Rust's `String` and `&str` are
**always valid UTF-8**, a guarantee checked when the text is created, and
everything about them follows from that. Some operations that look simple in
other languages, such as "the character at position 3", are deliberately
explicit here, because in UTF-8 they are not simple. This lesson collects the
tools for working with text correctly, which the exercise then tests with
accented and Japanese text.

## Background: what UTF-8 is

Computers store text as numbers. **Unicode** gives every character in every
writing system a number, its **code point**: `h` is 104, `é` is 233, `日` is
26085, `😀` is 128512. **UTF-8** is a way to store those numbers as bytes, using
one to four bytes per character:

| Character | Code point | UTF-8 bytes |
|---|---|---|
| `h` | 104 | 1: `68` |
| `é` | 233 | 2: `C3 A9` |
| `日` | 26085 | 3: `E6 97 A5` |
| `😀` | 128512 | 4: `F0 9F 98 80` |

(Bytes in hexadecimal.) The first 128 code points, plain English letters,
digits and punctuation, take one byte each, exactly as in the older ASCII
encoding. That is why UTF-8 won, and also why English-only tests miss the
bugs this lesson is about.

So `"héllo"` is 5 characters but 6 bytes:

```text
 bytes:  68 | C3 A9 | 6C | 6C | 6F
 index:  0    1  2    3    4    5
 chars:  h  |   é   |  l |  l |  o
```

## Bytes, chars, graphemes

There are three different things you might mean by "length", and Rust gives
each one its own method:

```rust
let s = "héllo";
s.len()               // 6: bytes
s.chars().count()     // 5: chars (code points)
s.bytes()             // an iterator of u8: 104, 195, 169, ...
s.chars()             // an iterator of char: 'h', 'é', 'l', ...
s.char_indices()      // (byte index, char) pairs: (0, 'h'), (1, 'é'), (3, 'l'), ...
```

(Expressions with their values.) `len()` is in bytes because that is what is
stored and what slicing uses; it is instant. `chars().count()` has to walk
the whole string to decode it.

A Rust `char` is one **Unicode scalar value**, a code point, always 4 bytes
in memory. That is still not always what a person sees as one character. A
"👍🏽" (thumbs up with a skin tone) is two `char`s, and an `é` can also be
written as `e` followed by a combining accent, again two `char`s. What a
reader perceives as one character is a **grapheme cluster**; counting those
needs the `unicode-segmentation` crate. For this lesson, "character" means
`char`.

## Slicing is by byte, and must land on a boundary

Slicing (`&s[a..b]`) uses byte positions, so it is fast. But a slice must
start and end **between** characters, never inside one, or the result would
not be valid UTF-8. Rust checks, and panics:

```rust
fn main() {
    let s = "héllo";
    println!("{}", &s[0..1]);    // "h": fine
    println!("{}", &s[0..2]);    // byte 2 is inside 'é'
}
```

```text
h
thread 'main' (4242) panicked at src/main.rs:4:22:
end byte index 2 is not a char boundary; it is inside 'é' (bytes 1..3 of string)
```

The message is precise: `é` occupies bytes 1 and 2 (the range `1..3`), so 2
is not a boundary. This is the bug in the exercise's starter code:
`truncate_chars` slices at `n` bytes, which works for English and panics on
the first accent.

The fix is never to compute byte positions by arithmetic, but to get them
from methods that know the encoding: `char_indices()` gives the byte index
of each character, and `find()`, `split_once()` and friends return positions
or pieces that are boundaries by construction. `s.is_char_boundary(i)`
checks one position. For example, the byte index where character number `n`
starts is `s.char_indices().nth(n)`: `Some((byte_index, ch))`, or `None` if
the string has `n` characters or fewer.

## Case and ASCII

Changing case also follows from Unicode. `to_uppercase()` returns a new
`String`, because the length can change: German `ß` has no single-character
upper case and becomes `SS`. For the same reason, `char::to_uppercase()`
returns an **iterator** of `char`s, not one `char`: `'ß'.to_uppercase()`
yields `'S'`, `'S'`. Collect it with `.collect::<String>()`, or print it
directly, since it implements `Display`.

For text that is ASCII by definition (protocol keywords, hex digits, HTTP
header names), the `_ascii_` methods (`to_ascii_lowercase`,
`eq_ignore_ascii_case`, `is_ascii_digit`) are faster and leave any non-ASCII
character alone. `s.is_ascii()` checks a whole string.

## Parsing

```rust
"42".parse::<i32>()                     // Ok(42), or Err(ParseIntError)
u8::from_str_radix("ff", 16)            // Ok(255): parse in base 16
"a,b,,c".split(',')                     // "a", "b", "", "c"
"  x  ".trim()                          // "x"
"key: value".split_once(": ")           // Some(("key", "value"))
"GET /x".strip_prefix("GET ")           // Some("/x"); None if it does not start so
```

(Expressions with their values.) `split` keeps empty pieces between two
separators, which is right for formats like CSV where an empty field means
something. `split_whitespace` (Beginner lesson 9) drops them.

`strip_prefix` returns `None` when the prefix is missing, so with `?` in a
function returning `Option` it reads as a check: `let hex = s.strip_prefix('#')?;`
means "if `s` does not start with `#`, the answer is `None`; otherwise
continue with the rest". Note that `from_str_radix` accepts both `ff` and
`FF`, and a leading `+`, so check the length and characters yourself if the
format is strict.

## Building strings

Building text in a loop with `+` or `format!` creates a new `String` each
time. Pushing into one `String` reuses its buffer:

```rust
use std::fmt::Write;                     // enables write! into a String

let mut out = String::with_capacity(64); // reserve room for 64 bytes up front
out.push_str("total: ");
out.push('=');
write!(out, "{:>8.2}", 3.14159).unwrap();
let joined = parts.join(", ");
```

(A fragment.) `with_capacity(64)` allocates once, so the pushes that follow
fit without reallocating. `write!` works like `format!` but appends to an
existing `String`; it needs the `std::fmt::Write` trait in scope, and
returns a `Result` that, for a `String`, can never be an error, hence the
`unwrap()`. `{:>8.2}` means right-aligned in 8 columns, 2 decimals. `join`
puts a separator between the items of a slice or `Vec` of strings.

## Cow: borrow when you can, own when you must

Consider a function that escapes `<` in text for HTML. Most inputs contain no
`<`, and the result equals the input. Returning `String` would copy every
input anyway, only to have an owned value to return. Returning `&str` is
impossible when a change was needed, since the new text has to live
somewhere.

`Cow` ("clone on write") holds **either** a borrowed value or an owned one,
and the caller can use it either way:

```rust
use std::borrow::Cow;

fn escape(s: &str) -> Cow<'_, str> {
    if s.contains('<') {
        Cow::Owned(s.replace('<', "&lt;"))     // had to build new text
    } else {
        Cow::Borrowed(s)                       // nothing to change: no copy
    }
}
```

`Cow<'_, str>` is an enum with two variants, `Borrowed(&str)` and
`Owned(String)`. The `'_` is the lifetime of the borrowed case, tied to `s`
by elision (Beginner lesson 12). `Cow` acts as a reference to its contents
whichever variant it is (it implements `Deref`, as smart pointers do), so
callers can call `&str` methods on it, print it, or compare it with `==`
without caring which one they got. If they need a `String`, `.into_owned()`
gives one, copying only if it was borrowed.

## Run it

```rust
use std::borrow::Cow;
use std::fmt::Write;

fn escape(s: &str) -> Cow<'_, str> {
    if s.contains('<') {
        Cow::Owned(s.replace('<', "&lt;"))
    } else {
        Cow::Borrowed(s)
    }
}

fn main() {
    let s = "héllo";
    println!("{} {}", s.len(), s.chars().count());
    println!("{:?}", s.char_indices().map(|(i, _)| i).collect::<Vec<_>>());
    println!("{} {}", &s[0..1], s.is_char_boundary(2));
    println!("{:?} {:?}", s.char_indices().nth(2), s.char_indices().nth(9));

    let upper = "straße".to_uppercase();
    println!("{upper} {} {}", upper.len(), 'ß'.to_uppercase());

    println!("{:?} {:?}", u8::from_str_radix("ff", 16), "a,b,,c".split(',').collect::<Vec<_>>());
    println!("{:?} {:?}", "key: value".split_once(": "), "GET /x".strip_prefix("GET "));

    let mut out = String::with_capacity(64);
    out.push_str("total:");
    write!(out, "{:>8.2}", 3.14159).unwrap();
    println!("[{out}]");

    for text in ["plain", "a<b"] {
        let e = escape(text);
        let kind = match &e {
            Cow::Borrowed(_) => "borrowed",
            Cow::Owned(_) => "owned",
        };
        println!("{e} {kind}");
    }
}
```

```output
6 5
[0, 1, 3, 4, 5]
h false
Some((3, 'l')) None
STRASSE 7 SS
Ok(255) ["a", "b", "", "c"]
Some(("key", "value")) Some("/x")
[total:    3.14]
plain borrowed
a&lt;b owned
```

The byte offsets jump from 1 to 3: `é` occupies bytes 1 and 2, which is why
byte 2 is not a boundary. Character number 2 (counting from 0) is the first
`l`, at byte 3. `"straße"` has 6 characters but its upper case has 7.

## Your turn

In `src/lib.rs`. The tests use accented and Japanese text throughout, so
anything that counts bytes where it means characters will fail.

- `char_count(s)`: the number of characters, not bytes. The starter returns
  `s.len()`; `"日本語"` must give 3, not 9.
- `truncate_chars(s, n)`: the first `n` characters, as a **slice of `s`**
  (the tests check that it points into the original string, so no new
  `String`). All of `s` if it has `n` characters or fewer; `""` for 0. The
  starter slices at byte `n`, which panics on `"héllo"`.
- `capitalize_words(s)`: upper-case the first character of each word, leave
  the rest of the word as it is:
  - `"élan vital"` gives `"Élan Vital"`
  - `"ßtraße"` gives `"SStraße"`: an upper-cased first character may become
    several
  - words are separated by single spaces and the spaces are kept exactly:
    `"a  b"` gives `"A  B"`. So split on `' '` (which yields an empty word
    between two spaces) rather than `split_whitespace`.
- `parse_rgb(s)`: `"#ff8000"` gives `Some((255, 128, 0))`; upper- and
  lower-case hex digits both work. Anything else gives `None`: no `#`, not
  exactly six characters after it, a non-hex character, or a non-ASCII one
  (`"#ff80é"` is six *bytes* after the `#`, so check `is_ascii()` before you
  slice it into pairs).
- `normalize_spaces(s)`: collapse each run of spaces into one space, and
  remove spaces at the start and end: `"too   many  spaces"` gives
  `"too many spaces"`, `"  padded  "` gives `"padded"`. Return
  `Cow::Borrowed(s)` when there is nothing to change (no double space, and
  no space at either end), and `Cow::Owned` otherwise.
