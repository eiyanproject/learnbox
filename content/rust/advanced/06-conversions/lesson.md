---
title: Conversions
summary: From and Into, TryFrom for checked conversions, FromStr for parsing, AsRef for flexible arguments, and Deref for smart wrappers.
order: 6
files: [src/lib.rs]
run: cargo test
hints:
  - "`impl TryFrom<u16> for Port { type Error = PortError; fn try_from(v: u16) -> Result<Self, PortError> { if v == 0 { Err(PortError::Zero) } else { Ok(Port(v)) } } }`."
  - "`impl FromStr for Rgb`: strip `rgb(` and `)`, `split(',')`, `trim` and `parse::<u8>()` each part, and require exactly three. Map every failure to `ParseRgbError`."
  - "`impl From<Rgb> for String` is what makes `let s: String = color.into()` work. You never implement `Into` directly."
  - "`total_len<S: AsRef<str>>(items: &[S]) -> usize` sums `s.as_ref().len()`. `NonEmptyVec` implements `Deref<Target = [T]>` returning `&self.0`, so slice methods like `len()` and `iter()` just work."
---

Rust never converts types implicitly. Instead, a small set of standard traits
names each kind of conversion, and implementing them makes your types work with
`?`, `.into()`, `.parse()` and generic APIs.

## From and Into

`From<T>` is an infallible conversion. Implementing it gives you `Into` for free:

```rust
struct Celsius(f64);

impl From<f64> for Celsius {
    fn from(v: f64) -> Self { Celsius(v) }
}

let a = Celsius::from(21.5);
let b: Celsius = 21.5.into();          // Into, provided automatically
```

Always implement `From`, never `Into`. You already saw that `?` uses `From` to
convert error types.

Accepting `impl Into<String>` makes an API take both `&str` and `String`:

```rust
fn new(name: impl Into<String>) -> User { User { name: name.into() } }
```

## TryFrom: conversions that can fail

```rust
use std::convert::TryFrom;

struct Percent(u8);

impl TryFrom<i32> for Percent {
    type Error = String;
    fn try_from(v: i32) -> Result<Self, Self::Error> {
        if (0..=100).contains(&v) { Ok(Percent(v as u8)) } else { Err(format!("{v} is not a percentage")) }
    }
}

let p: Result<Percent, _> = 42.try_into();
```

This is the checked alternative to `as`, which silently truncates (`300_i32 as u8`
is 44). Standard numeric types implement it: `u8::try_from(300_i32)` is an `Err`.

## FromStr: what .parse() calls

```rust
use std::str::FromStr;

impl FromStr for Point {
    type Err = ParsePointError;
    fn from_str(s: &str) -> Result<Self, Self::Err> { ... }
}

let p: Point = "3,4".parse()?;
```

## AsRef: cheap borrowed views

`AsRef<str>` means "can be viewed as a `&str` cheaply". Functions that only
need to read accept any of `&str`, `String`, `&String`...

```rust
fn shout<S: AsRef<str>>(s: S) -> String { s.as_ref().to_uppercase() }
```

`AsRef<Path>` is why `File::open` accepts strings, `PathBuf`s and `&Path`.

## Deref: acting like what you wrap

Implementing `Deref` lets a wrapper be used like its contents: method calls and
`&wrapper` auto-dereference:

```rust
use std::ops::Deref;

struct Name(String);

impl Deref for Name {
    type Target = str;
    fn deref(&self) -> &str { &self.0 }
}

let n = Name("Ana".into());
n.len();                        // str::len through Deref
```

Use it for smart-pointer-like wrappers that add a guarantee (non-empty,
validated, sorted). Do not use it to fake inheritance.

## Your turn

In `src/lib.rs`:

- `Port(u16)` with `TryFrom<u16>`: `0` is `PortError::Zero`
- `Rgb { r, g, b }` with `FromStr` parsing `"rgb(255, 128, 0)"` (spaces optional)
  into a value, or `ParseRgbError` for anything else; and `From<Rgb> for String`
  producing `"#ff8000"`
- `Celsius` and `Fahrenheit` newtypes over `f64` with `From` in both directions
- `total_len(items)`: total byte length of a slice of anything `AsRef<str>`
- `NonEmptyVec<T>`: `NonEmptyVec::new(vec)` returns `None` for an empty vector;
  `first()` returns `&T` (no `Option`: it cannot be empty), and `Deref` to `[T]`
