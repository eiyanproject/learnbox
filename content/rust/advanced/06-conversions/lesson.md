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
  - "`total_len<S: AsRef<str>>(items: &[S]) -> usize` sums `s.as_ref().len()`. `NonEmptyVec` implements `Deref<Target = [T]>` returning `&self.0`, so slice methods like `len()` and `iter()` work on it."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **conversion trait** | one standard trait per kind of conversion |
| **`From<T>`** | a conversion from `T` that always succeeds |
| **`Into<T>`** | the same seen from the other side; free from every `From`, so implement `From` only |
| **blanket impl** | `impl<T, U: From<T>> Into<U> for T`, which gives the free `Into` |
| **orphan rule** | you may implement `From<Rgb> for String` because `Rgb` is yours |
| **`TryFrom`** / **`TryInto`** | a conversion that can fail, returning a `Result` |
| **truncation** | `as` between integers keeps only the low bits: `300 as u8` is 44 |
| **prelude** | names available without `use`; `TryFrom` is there since the 2021 edition |
| **`FromStr`** | what `.parse()` calls; its error type is called `Err` |
| **`AsRef<T>`** | can be viewed cheaply as a `&T`; for read-only arguments |
| **`Deref`** | lets a wrapper act like its contents |
| **auto-deref** | methods the wrapper lacks are looked up on its `Target` |
| **deref coercion** | a `&Name` converting to `&str` where one is expected |
| **newtype** | a one-field struct such as `Celsius(f64)`, a distinct type |
| **invariant-carrying wrapper** | a wrapper that adds a guarantee, such as "never empty" |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `impl From<Celsius> for Fahrenheit { fn from(c: Celsius) -> Self { ... } }` | a `From` impl |
| `let f: Fahrenheit = c.into();` | the free `Into` |
| `fn new(name: impl Into<String>)` | accepts `&str` and `String` |
| `impl TryFrom<u16> for Port { type Error = PortError; fn try_from(v: u16) -> Result<Self, Self::Error> }` | a fallible conversion |
| `u8::try_from(300_i32)` | `Err` instead of truncating |
| `impl FromStr for Rgb { type Err = ParseRgbError; fn from_str(s: &str) -> Result<Self, Self::Err> }` | makes `.parse()` work |
| `s.strip_prefix("rgb(")?.strip_suffix(')')` | peel off the wrapper text |
| `part.trim().parse::<u8>()` | rejects values above 255 |
| `format!("#{:02x}{:02x}{:02x}", r, g, b)` | two lower-case hex digits per channel |
| `fn total_len<S: AsRef<str>>(items: &[S]) -> usize` | reads any kind of string |
| `impl<T> Deref for NonEmptyVec<T> { type Target = [T]; fn deref(&self) -> &[T] }` | acts like a slice |

### Errors

| Error | Means |
|---|---|
| `error[E0277]: the trait bound String: From<Rgb> is not satisfied` | `.into()` without the `From` impl |
| `type annotations needed` | `.into()` with no target type to convert to |
| `ParseIntError` | a part that is not a number, or too big for `u8` |

---

Rust never converts between types on its own. An `i32` is not silently
widened to an `i64`, a `&str` does not quietly become a `String`, and your
`Celsius` will not turn into a `Fahrenheit` unless you write the formula.
That avoids a whole family of bugs, but it would make code verbose if every
conversion were a differently named function.

Instead, the standard library defines a small set of **conversion traits**,
one for each *kind* of conversion. Implement the right one for your type,
and it works with everything built on that trait: `?`, `.into()`,
`.parse()`, `.try_into()`, and any generic function that accepts "anything
convertible to X". This lesson goes through them:

| Trait | Kind of conversion | You get |
|---|---|---|
| `From<T>` / `Into<T>` | always succeeds, may cost (allocation, arithmetic) | `X::from(t)`, `t.into()`, and `?` error conversion |
| `TryFrom<T>` / `TryInto<T>` | may fail | `X::try_from(t)`, `t.try_into()`, both returning `Result` |
| `FromStr` | parse from text, may fail | `"...".parse::<X>()` |
| `AsRef<T>` | a cheap borrowed view | functions that accept many argument types |
| `Deref` | a wrapper that acts like what it wraps | the inner type's methods on the wrapper |

## From and Into

`From<T>` is a conversion **from** `T` that always succeeds:

```rust
struct Celsius(f64);

impl From<f64> for Celsius {
    fn from(v: f64) -> Self {
        Celsius(v)
    }
}

let a = Celsius::from(21.5);
let b: Celsius = 21.5.into();          // Into, provided automatically
```

(A fragment.) `Into<T>` is the same conversion seen from the other side:
`x.into()` means "convert `x` into whatever type is expected here". The
standard library has a blanket impl (Intermediate lesson 3),
`impl<T, U: From<T>> Into<U> for T`, so every `From` gives you the matching
`Into` for free. Hence the rule: **implement `From`, never `Into`.**

`.into()` needs to know the target type, from an annotation (`let b:
Celsius`), a parameter type, or a return type. When the conversion does not
exist, the error names the `From` impl that is missing, even though you
called `into`:

```text
error[E0277]: the trait bound `String: From<Rgb>` is not satisfied
 --> src/lib.rs:2:32
  |
2 | pub fn f(c: Rgb) -> String { c.into() }
  |                                ^^^^ the trait `From<Rgb>` is not implemented for `String`
  |
  = note: required for `Rgb` to implement `Into<String>`
```

The exercise needs exactly this impl: `impl From<Rgb> for String`. The
orphan rule (Intermediate lesson 3) allows it: `String` is not yours, but
`Rgb` is.

`From` is also what `?` uses to convert errors (Intermediate lesson 2). And
`Into` is handy for accepting flexible arguments: a function taking
`impl Into<String>` accepts both `"Ana"` and `String::from("Ana")`, and only
allocates when it was given a `&str`:

```rust
fn new(name: impl Into<String>) -> User {
    User { name: name.into() }
}
```

## TryFrom: conversions that can fail

Some conversions only work for some values: not every `i32` is a valid
percentage, and not every `u16` a valid port. `TryFrom` returns a `Result`,
with an associated type for the error:

```rust
struct Percent(u8);

impl TryFrom<i32> for Percent {
    type Error = String;
    fn try_from(v: i32) -> Result<Self, Self::Error> {
        if (0..=100).contains(&v) {
            Ok(Percent(v as u8))
        } else {
            Err(format!("{v} is not a percentage"))
        }
    }
}

let p: Result<Percent, _> = 42.try_into();
```

(A fragment.) As with `From` and `Into`, `TryInto` comes free from
`TryFrom`. Both are in the prelude in the 2021 edition and later, so no `use`
is needed.

This is the checked alternative to `as`. `as` between integer types never
fails, and when the value does not fit, it silently keeps only the low bits:
`300_i32 as u8` is 44 (300 - 256). The standard numeric types implement
`TryFrom` for each other, so `u8::try_from(300_i32)` is an `Err` instead.
Use `as` only when you know the value fits, or truncation is what you want.

## FromStr: what .parse() calls

`str::parse::<X>()` works for any `X` that implements `FromStr`. Implement it
and your type can be parsed like a number:

```rust
use std::str::FromStr;

impl FromStr for Point {
    type Err = ParsePointError;
    fn from_str(s: &str) -> Result<Self, Self::Err> { ... }
}

let p: Point = "3,4".parse()?;
```

(A fragment.) Note the associated type is called `Err` here, not `Error` as
in `TryFrom`: a historical accident, but the compiler insists. Parsing is
usually a series of steps that can each fail, which `?` keeps flat. The
`Point` parser in the program below shows the pattern:
`split_once(',').ok_or("no comma")?`, then `trim().parse().map_err(...)?` for
each half.

## AsRef: accepting many argument types

`AsRef<T>` means "can be viewed as a `&T`, cheaply, without allocating". A
function that only needs to *read* a string can accept anything that
`AsRef<str>`:

```rust
fn shout<S: AsRef<str>>(s: S) -> String {
    s.as_ref().to_uppercase()
}

shout("hi");                    // &str
shout(String::from("there"));   // String
```

(A fragment.) `&str`, `String`, `&String`, `Box<str>` and `Cow<str>` all
implement `AsRef<str>`. This is why `File::open` accepts `"notes.txt"`, a
`String` and a `PathBuf` alike: its parameter is `impl AsRef<Path>`.

Compared with `Into<String>`: use `AsRef` when you only read the value, and
`Into` when you need to **own** it (store it in a struct).

## Deref: a wrapper that acts like its contents

Intermediate lesson 5 mentioned that smart pointers act like references to
what they hold, through the `Deref` trait. You can implement it for your own
wrappers:

```rust
use std::ops::Deref;

struct Name(String);

impl Deref for Name {
    type Target = str;
    fn deref(&self) -> &str {
        &self.0
    }
}

let n = Name("Ana".into());
n.len();                        // str::len, found through Deref
```

(A fragment.) `type Target = str` says what the wrapper acts like. Whenever
you call a method that `Name` itself does not have, the compiler tries
`n.deref().len()`, and so on through further `Deref`s if needed; this is
called **auto-deref**. A `&Name` also converts to `&str` where one is
expected (**deref coercion**).

Methods defined on the wrapper itself are found **first**. That is what lets
the exercise's `NonEmptyVec` have its own `first()` returning `&T`, while a
slice's `first()` returns `Option<&T>`: `v.first()` finds the wrapper's
method before looking through `Deref`. (Inside that method, `self.0.first()`
or `&self.0[0]` reaches the slice's version.)

Use `Deref` for wrappers that **add a guarantee** to what they wrap and
should otherwise behave like it: a vector that is never empty, a string that
is known to be valid. Do not use it to imitate inheritance between unrelated
types; that makes it hard to see where a method comes from.

## Run it

```rust
use std::ops::Deref;
use std::str::FromStr;

struct Celsius(f64);

impl From<f64> for Celsius {
    fn from(v: f64) -> Self {
        Celsius(v)
    }
}

struct Percent(u8);

impl TryFrom<i32> for Percent {
    type Error = String;
    fn try_from(v: i32) -> Result<Self, Self::Error> {
        if (0..=100).contains(&v) {
            Ok(Percent(v as u8))
        } else {
            Err(format!("{v} is not a percentage"))
        }
    }
}

#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

impl FromStr for Point {
    type Err = String;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let (a, b) = s.split_once(',').ok_or("no comma")?;
        let x = a.trim().parse().map_err(|_| "bad x")?;
        let y = b.trim().parse().map_err(|_| "bad y")?;
        Ok(Point { x, y })
    }
}

struct Name(String);

impl Deref for Name {
    type Target = str;
    fn deref(&self) -> &str {
        &self.0
    }
}

fn shout<S: AsRef<str>>(s: S) -> String {
    s.as_ref().to_uppercase()
}

fn main() {
    let b: Celsius = 21.5.into();                 // Into, from our From
    println!("{}", b.0);

    let ok: Result<Percent, _> = 42.try_into();
    println!("{} {:?}", ok.unwrap().0, Percent::try_from(250).err());
    println!("{} {}", 300_i32 as u8, u8::try_from(300_i32).is_err());

    println!("{:?} {:?}", "3, 4".parse::<Point>(), "3".parse::<Point>().err());
    println!("{} {}", shout("hi"), shout(String::from("there")));

    let n = Name("Ana".into());
    println!("{} {}", n.len(), n.to_uppercase()); // str methods, through Deref
}
```

```output
21.5
42 Some("250 is not a percentage")
44 true
Ok(Point { x: 3, y: 4 }) Some("no comma")
HI THERE
3 ANA
```

`"no comma"` is a `&str`, and `?` converted it to the `String` error type
through `From<&str> for String`: the same `From` machinery again. `300 as u8`
kept the low 8 bits, 44; `try_from` refused. `Name` has no `len` or
`to_uppercase` of its own; both came from `str` through `Deref`.

## Your turn

In `src/lib.rs`:

- `TryFrom<u16> for Port`: every value except 0 is a valid port;
  `Port::try_from(0)` is `Err(PortError::Zero)`
- `FromStr for Rgb`: parse `"rgb(255, 128, 0)"` into `Rgb { r: 255, g: 128,
  b: 0 }`. Spaces after the commas are optional (`"rgb(1,2,3)"` works).
  Everything else is `Err(ParseRgbError)`, including:
  - a value above 255 (`"rgb(256, 0, 0)"`: let `parse::<u8>()` reject it)
  - two or four numbers instead of three
  - a missing `rgb` prefix (`"(1, 2, 3)"`) or closing `)` (`"rgb(1, 2, 3"`)
  - non-numbers, and the empty string
- `From<Rgb> for String`: `"#"` and each channel as two lower-case hex
  digits: `"#ff8000"`, and `"#000aab"` for `(0, 10, 171)` (`{:02x}`)
- `Celsius` and `Fahrenheit` (newtypes over `f64`) with `From` in **both**
  directions: F = C × 9 / 5 + 32, C = (F − 32) × 5 / 9. `Celsius(100.0)`
  becomes `Fahrenheit(212.0)`, and −40 is the same in both.
- `total_len(items)`: the total byte length of a slice of anything that is
  `AsRef<str>`; the tests pass both `String`s and `&str`s
- `NonEmptyVec<T>`:
  - `new(vec)` returns `None` for an empty vector, `Some` otherwise
  - `first(&self) -> &T`, with no `Option`, since there is always a first
    item
  - `Deref<Target = [T]>`, so `len()`, `iter()` and `contains()` work on it
