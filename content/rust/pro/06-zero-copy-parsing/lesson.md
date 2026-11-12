---
title: Zero-copy parsing
summary: Parse into borrowed slices instead of owned Strings, keep lifetimes straight, and reach for Cow only when a value must change.
order: 6
files: [src/lib.rs]
run: cargo test
hints:
  - "`LogEntry<'a>` holds `&'a str` fields. `parse_line` uses `split_once(' ')` twice and then `split_once(\": \")`, returning slices of the input; no `to_string()` anywhere."
  - "`parse_query`: split the string on `'&'`, then each pair on `'='`; return `Vec<(&'a str, Cow<'a, str>)>` where the value borrows unless it contains `%` or `+`, which must be decoded."
  - "`Csv::rows` returns an iterator over `Vec<&'a str>` per line: `self.text.lines().map(|line| line.split(self.sep).map(str::trim).collect())`."
  - "`longest_field` compares `str::len` and returns the winning slice; `as_ptr` in the tests proves it points into the original text."
---

A typical parser reads some text and builds a struct with a `String` for
every field: copy the timestamp, copy the level, copy the message. Each copy
is a heap allocation (lesson 5), and for a log processor reading millions of
lines, those copies can cost more than the parsing itself.

But when the whole input is already in memory, the fields are **already
there**, in the input. Instead of copying them, a parser can return `&str`
slices pointing into the input. This is called **zero-copy parsing**, and it
is how `serde_json`'s borrowed mode, the `httparse` HTTP parser, and most
high-volume log processors work. Rust is unusually good at it, because the
borrow checker guarantees that none of those slices outlive the text they
point into: the classic danger of the technique in C, a pointer into a freed
buffer, cannot compile.

## Borrowed structs

A struct whose fields borrow from the input carries the input's lifetime
(Intermediate lesson 10):

```rust
pub struct Entry<'a> {
    pub level: &'a str,
    pub message: &'a str,
}

fn parse<'a>(line: &'a str) -> Option<Entry<'a>> {
    let (level, message) = line.split_once(": ")?;
    Some(Entry { level, message })
}
```

(A fragment.) `split_once` returns two slices of `line`, and the `Entry`
just keeps them. The signature says the `Entry` borrows from `line`, so the
compiler will not let it be used after `line` is gone. With elision (one
input reference, so the output gets its lifetime) it can be written
`fn parse(line: &str) -> Option<Entry<'_>>`, where `'_` means "the elided
lifetime". In memory:

```text
 line:     "WARN: disk at 91%"
            ^^^^  ^^^^^^^^^^^^
 Entry {   level   message     }    two (pointer, length) pairs, no copies
```

Each `&str` is 16 bytes, a pointer and a length, whatever the size of the
text it refers to. The tests check that your slices point into the original
input by comparing addresses with `as_ptr()`: a copied `String` would have a
different address.

## The splitting toolkit

None of these allocate; they all return slices of the input, or iterators of
slices:

```rust
text.lines()                       // each line, without \n or \r\n
text.split(',')                    // the pieces between commas
text.splitn(3, ',')                // at most 3 pieces; the last holds the rest
text.split_once(": ")              // Some((before, after)) at the first ": "
text.rsplit_once('=')              // the same at the last '='
text.split_whitespace()            // words
text.trim()   text.strip_prefix("GET ")
&text[a..b]                        // by byte position (Intermediate lesson 7)
```

(Expressions on some `text: &str`.) Chaining `split_once` is a handy way to
take fields off the front one at a time, with `?` giving up as soon as one is
missing:

```rust
let (timestamp, rest) = line.split_once(' ')?;
let (level, rest) = rest.split_once(' ')?;
```

Each step leaves the unparsed remainder in `rest`, still a slice of the same
line. The last field can then contain anything, including spaces and colons,
because nothing splits it further.

## When you must own

Sometimes a value is not in the input as-is. URL query strings encode a space
as `+` and other characters as `%` followed by two hex digits (`%2F` is `/`);
JSON strings escape a newline as `\n`. The decoded text exists nowhere in the
input, so it cannot be a slice of it.

`Cow<'a, str>` (Intermediate lesson 7) handles that case without giving up
zero-copy for the rest: borrow when the value needs no change, which is
usually, and allocate only when it does:

```rust
fn decode(raw: &str) -> Cow<'_, str> {
    if raw.contains('%') || raw.contains('+') {
        Cow::Owned(percent_decode(raw))
    } else {
        Cow::Borrowed(raw)
    }
}
```

(A fragment; `percent_decode` is yours to write in the exercise.) Decoding
`%XX`: take the two characters after the `%`, parse them as a hex byte with
`u8::from_str_radix(.., 16)`, and push that byte as a `char` (fine for ASCII,
which is what the tests use). Callers of a `Cow`-returning parser get the
best of both: no allocation for plain input, correct values for the rest.

## The trade-off

Zero-copy has one requirement: **the input must outlive everything parsed
from it**. That fits naturally when you read a file or a request body into
one buffer, process it, and move on. It fits badly when parsed values are
kept for later, sent through a channel, or handed to another thread, while
the buffer is reused or dropped. The compiler will refuse those programs
(with lifetime errors like Intermediate lesson 10's), and the fix is to own
the data: copy just the fields you keep with `.to_string()`, or call
`.into_owned()` on a `Cow`.

Do not force it everywhere. A `String` per field is perfectly fine in code
that runs once per request. Reach for zero-copy in hot loops and on large
inputs, where the allocations show up when you measure.

## Run it

```rust
use std::borrow::Cow;

struct Entry<'a> {
    level: &'a str,
    message: &'a str,
}

fn parse(line: &str) -> Option<Entry<'_>> {
    let (level, message) = line.split_once(": ")?;
    Some(Entry { level, message })
}

fn decode(raw: &str) -> Cow<'_, str> {
    if raw.contains('+') {
        Cow::Owned(raw.replace('+', " "))
    } else {
        Cow::Borrowed(raw)
    }
}

fn main() {
    let text = String::from("INFO: started\nWARN: disk at 91%\nnot a log line");
    let entries: Vec<Entry> = text.lines().filter_map(parse).collect();
    for e in &entries {
        println!("[{}] {}", e.level, e.message);
    }

    // the message is a window into `text` itself: same memory, 6 bytes in
    let offset = entries[0].message.as_ptr() as usize - text.as_ptr() as usize;
    println!("{offset}");

    for raw in ["plain", "a+b"] {
        let d = decode(raw);
        println!("{d} {}", matches!(d, Cow::Borrowed(_)));
    }
    println!("{:?}", "a=b=c".rsplit_once('='));
}
```

```output
[INFO] started
[WARN] disk at 91%
6
plain true
a b false
Some(("a=b", "c"))
```

`filter_map(parse)` dropped the line without `": "`. The first message starts
6 bytes into `text`, right after `INFO: `: it is the same memory, not a copy.
Only `"a+b"` needed decoding, so only it was `Owned`.

## Your turn

In `src/lib.rs`, without any `to_string()` (or other copying) on the parsing
path:

- `parse_line(line) -> Option<LogEntry<'_>>` for lines like
  `2026-09-18T01:20:56Z ERROR db: connection lost`. The format is: a
  timestamp, a space, a level, a space, a **target** directly followed by
  `": "`, then the message, which is everything after that and may contain
  spaces and colons (`"t L target: a: b c"` has the message `"a: b c"`).
  Return `None` for a malformed line, including:
  - an empty line, or one with fewer fields (`"only-one-field"`)
  - no `": "` after the target (`"ts LEVEL no-colon"`)
  - a target containing a space (`"ts LEVEL two words: x"`)

  All four fields are slices of `line`: the tests check the timestamp's
  address.
- `errors_only(text)`: the entries of all valid lines whose level is
  exactly `"ERROR"`, skipping invalid lines, borrowed from `text`
- `parse_query(query)`: split `a=1&b=hello+world&c=%2Fpath` on `&` into
  `(key, value)` pairs, the value a `Cow<str>`:
  - `Cow::Borrowed` when the value contains no `+` and no `%`
  - otherwise `Cow::Owned`, decoded: `+` becomes a space, `%XX` becomes the
    byte with hex value `XX` (`%2F` is `/`)
  - `c=` gives an empty value; a key with no `=` at all (`flag`) gives
    `("flag", Cow::Borrowed(""))`
- `Csv<'a>` (given: the text and a separator):
  - `rows()`: an iterator yielding, for each non-empty line, a `Vec<&'a str>`
    of its fields, each **trimmed**, so `"name, score"` gives `["name",
    "score"]`. Return it as `impl Iterator<Item = Vec<&'a str>> + '_`.
  - `column(name)`: the values in the column whose header (first row) is
    `name`, from every row after the header; an empty `Vec` if there is no
    such column or no text
- `longest_field(text, sep)`: the longest trimmed field on any line, as a
  slice of `text`; `""` for empty text
