---
title: Designing errors
summary: A custom error enum with Display and std::error::Error, From conversions so ? just works, source chains, and Box<dyn Error> at the top.
order: 2
files: [src/lib.rs]
run: cargo test
hints:
  - "`ConfigError` has variants `Missing(String)`, `InvalidNumber { key: String, source: ParseIntError }` and `OutOfRange { key: String, value: i64 }`, with `#[derive(Debug)]`."
  - "`impl fmt::Display for ConfigError`: one `match self` arm per variant, using `write!(f, ...)` with the exact messages from the lesson."
  - "`impl std::error::Error for ConfigError { fn source(&self) -> Option<&(dyn Error + 'static)> { match self { Self::InvalidNumber { source, .. } => Some(source), _ => None } } }`."
  - "`get_port`: `let raw = config.get(\"port\").ok_or_else(|| ConfigError::Missing(\"port\".into()))?;` then `raw.trim().parse::<i64>().map_err(|source| ConfigError::InvalidNumber { key: \"port\".into(), source })?`, then the range check."
---

The Beginner track used `Result<T, String>`. Strings are fine for a quick
program, but callers cannot tell errors apart without parsing text. Libraries
define their own error **types**.

## An error enum

```rust
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
pub enum LoadError {
    NotFound(String),
    BadNumber { line: usize, source: ParseIntError },
}
```

Each variant is one thing that can go wrong, carrying the data a caller needs
to react or to report it.

## Display and Error

Implement `Display` for the human-readable message, and the `Error` trait so
the type works with the rest of the ecosystem:

```rust
impl fmt::Display for LoadError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            LoadError::NotFound(path) => write!(f, "file not found: {path}"),
            LoadError::BadNumber { line, .. } => write!(f, "bad number on line {line}"),
        }
    }
}

impl std::error::Error for LoadError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            LoadError::BadNumber { source, .. } => Some(source),
            _ => None,
        }
    }
}
```

`source()` links to the underlying cause, so tools can print the whole chain:
"bad number on line 3", caused by "invalid digit found in string".

## From: making ? convert for you

`?` calls `From::from` on the error. Implement `From` and lower-level errors
convert automatically:

```rust
impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self {
        AppError::Io(e)
    }
}

fn read_config() -> Result<String, AppError> {
    let text = std::fs::read_to_string("app.toml")?;   // io::Error -> AppError
    Ok(text)
}
```

When the conversion needs extra context (which key? which line?), use
`map_err` instead: `s.parse().map_err(|source| MyError::Bad { key, source })?`.

## Box<dyn Error>: the application boundary

Applications (as opposed to libraries) often just need "some error, printable":

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let port = get_port(&config)?;       // any error type implementing Error converts
    Ok(())
}
```

A rule of thumb: libraries return precise enums; `main` and top-level glue use
`Box<dyn Error>` (the popular `thiserror` and `anyhow` crates automate these two
styles).

## Your turn

In `src/lib.rs`, with configuration given as a `HashMap<String, String>`:

- `ConfigError` with variants `Missing(String)`,
  `InvalidNumber { key: String, source: ParseIntError }` and
  `OutOfRange { key: String, value: i64 }`, deriving `Debug`
- `Display` messages: `missing key: port`, `port is not a number`,
  `port out of range: 70000`
- `Error` with `source()` returning the `ParseIntError` for `InvalidNumber`
- `get_port(config)`: the `"port"` key as `u16`, 1 to 65535 (whitespace trimmed)
- `get_workers(config)`: the `"workers"` key, defaulting to `4` when missing;
  otherwise parsed like the port and within 1 to 64
- `load(config)`: returns `Result<(u16, u16), Box<dyn Error>>` using `?` on both
