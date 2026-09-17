---
title: Zero-copy parsing
summary: Parse into borrowed slices instead of owned Strings, keep lifetimes straight, and reach for Cow only when a value must change.
order: 6
files: [src/lib.rs]
run: cargo test
hints:
  - "`LogEntry<'a>` holds `&'a str` fields. `parse_line` uses `split_once(' ')` repeatedly (or `splitn(4, ' ')`) and returns slices of the input; no `to_string()` anywhere."
  - "`parse_query`: split the string on `'&'`, then each pair on `'='`; return `Vec<(&'a str, Cow<'a, str>)>` where the value borrows unless it contains `%20` or `+`, which must be decoded."
  - "`Csv::rows` returns an iterator over `Vec<&'a str>` per line: `self.text.lines().map(|line| line.split(self.sep).collect())`."
  - "`longest_field` compares `str::len` and returns the winning slice; `as_ptr` in the tests proves it points into the original text."
---

A parser that builds a `String` for every field allocates constantly. When the
input text is already in memory, the fields are **already there**: return `&str`
slices into it instead. This is what `serde_json`'s borrowed mode, `httparse`
and most log processors do.

## Borrowed structs

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

`Entry<'a>` cannot outlive the text it points into; the compiler enforces that.
The elision rules make the signature `fn parse(line: &str) -> Option<Entry<'_>>`
in practice.

## The splitting toolkit

None of these allocate; they all return slices of the input:

```rust
text.lines()
text.split(',')          text.splitn(3, ',')      text.rsplit_once('=')
text.split_once(": ")    text.split_whitespace()
text.trim()              text.strip_prefix("GET ")
&text[a..b]
```

## When you must own

Some values genuinely change during parsing: percent-decoding `%20`, unescaping
`\n`, lower-casing. `Cow<'a, str>` lets you borrow in the common case and
allocate only for the rest:

```rust
fn decode(raw: &str) -> Cow<'_, str> {
    if raw.contains('%') || raw.contains('+') {
        Cow::Owned(percent_decode(raw))
    } else {
        Cow::Borrowed(raw)
    }
}
```

A parser returning `Cow` gives callers the best of both: no allocation for plain
input, correctness for the rest.

## The trade-off

Zero-copy means the **input must outlive the parsed values**. That is natural
when you read a file or a request body into one buffer and process it before
moving on. It does not fit when parsed values are stored for later, put on a
channel, or sent to another thread with a shorter-lived buffer. Then own the
data (or use `Cow` and call `.into_owned()`).

Do not force it everywhere: a `String` per field is fine in code that runs once
per request. Reach for zero-copy in hot loops and large inputs.

## Your turn

In `src/lib.rs`, without a single `to_string()` in the parsing path:

- `LogEntry<'a> { timestamp, level, target, message }` and
  `parse_line(line) -> Option<LogEntry<'_>>` for
  `2026-09-18T01:20:56Z ERROR db: connection lost`; the message may contain
  spaces and colons; a malformed line is `None`
- `errors_only(text)`: entries with level `"ERROR"`, borrowed from `text`
- `parse_query(query)`: `a=1&b=hello+world&c=%2Fpath` into pairs where the value
  is `Cow::Borrowed` unless it contained `+` or `%XX` (decode those)
- `Csv<'a>`: `new(text, sep)`, `rows()` yielding `Vec<&'a str>`, and
  `column(name)` returning the values of a named column from the header row
- `longest_field(text, sep)`: the longest field anywhere in the text, as a slice
