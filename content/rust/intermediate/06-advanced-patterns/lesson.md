---
title: Patterns in depth
summary: Slice patterns, @ bindings, nested destructuring, match guards, let-else and matches!.
order: 6
files: [src/lib.rs]
run: cargo test
hints:
  - "`describe_slice`: `match items { [] => ..., [one] => ..., [first, .., last] => ... }`. A two-item slice also matches `[first, .., last]` with `..` empty."
  - "`classify_age`: `match age { 0 => \"newborn\", 1..=12 => \"child\", teen @ 13..=19 => ..., _ => \"adult\" }`, where the teen arm formats `teen`."
  - "`parse_kv`: `let Some((key, value)) = line.split_once('=') else { return None; };` then trim both and reject an empty key."
  - "`total_shipping`: iterate `for order in orders` and `match order { Order { items, destination: Destination::Domestic { express: true }, .. } => ..., ... }`."
---

Beginner lesson 7 used patterns to recognise enum variants, numbers and
ranges. Patterns can do much more: take apart slices by shape, test a value
and keep it in the same breath, reach several levels into nested data, and
replace a nested `if let` with a flat early exit. Code that would otherwise
be a ladder of `if`s and index checks often becomes a short `match` that
reads like a table of cases, and the compiler still checks that the table is
complete.

A reminder of the vocabulary: a pattern either fits a value or not, and when
it fits, it may **bind** parts of the value to names. A pattern that always
fits, such as `x` or `(a, b)` for a pair, is **irrefutable**; one that can
fail, such as `Some(x)`, is **refutable**.

## Slice patterns

A slice can be matched by its shape, with each position being a pattern:

```rust
fn summary(xs: &[i32]) -> String {
    match xs {
        [] => "empty".into(),
        [x] => format!("just {x}"),
        [first, second] => format!("{first} and {second}"),
        [first, .., last] => format!("{first} ... {last}"),   // .. matches any number
    }
}
```

- `[]` fits only the empty slice; `[x]` exactly one item, bound to `x`;
  `[first, second]` exactly two.
- `..` inside a slice pattern stands for "any number of items here,
  including none", and may appear once. `[first, .., last]` fits any slice
  of at least two items. Here the two-item case was caught one arm earlier,
  so this arm only sees three or more. Remove the `[first, second]` arm, and
  a two-item slice matches `[first, .., last]` with `..` covering nothing.

Exhaustiveness still applies. Leave out the last arm and the compiler gives
the shape it is missing, in pattern syntax:

```text
error[E0004]: non-exhaustive patterns: `&[_, _, _, ..]` not covered
  |
2 |     match xs {
  |           ^^ pattern `&[_, _, _, ..]` not covered
```

That is, "a slice of three or more items". (`_` matches one item without
binding it.)

`name @ ..` binds the part covered by `..` as a **sub-slice**:

```rust
fn sum(xs: &[i32]) -> i32 {
    match xs {
        [] => 0,
        [head, rest @ ..] => head + sum(rest),
    }
}
```

(A fragment.) `head` is the first item and `rest` a slice of everything
after it. `sum(&[1, 2, 3])` is `1 + sum(&[2, 3])`, which is
`1 + 2 + sum(&[3])`, and so on down to `sum(&[])`, which is 0: each call
peels off one item until the empty-slice arm ends the recursion.

## @ bindings

A range pattern like `1..=1023` tests the value but does not bind it. `@`
does both: `name @ pattern` means "if it fits `pattern`, also bind the whole
value to `name`":

```rust
match port {
    p @ 1..=1023 => format!("privileged port {p}"),
    p @ 1024..=49151 => format!("registered port {p}"),
    p => format!("dynamic port {p}"),
}
```

(A fragment, with `port: u16`.) Without `@`, the arm would have to repeat
`port`, which works here but not when the matched value is a field deep
inside a pattern. The last arm, a bare `p`, fits everything (it is
irrefutable), so it acts like `_` while still binding the value. Port 0 lands
there too.

## Nested destructuring

Patterns nest: a pattern for a struct may contain patterns for its fields,
which may be enums with patterns for their fields, and so on:

```rust
struct Point { x: i32, y: i32 }
enum Shape { Circle { center: Point, radius: u32 }, Line(Point, Point) }

match shape {
    Shape::Circle { center: Point { x: 0, y: 0 }, radius } => format!("centred, r={radius}"),
    Shape::Circle { radius, .. } => format!("r={radius}"),
    Shape::Line(Point { x: x1, .. }, Point { x: x2, .. }) if x1 == x2 => "vertical".into(),
    Shape::Line(..) => "line".into(),
}
```

(A fragment.) Arm by arm:

1. A circle whose `center` field is a `Point` with `x` exactly 0 and `y`
   exactly 0; `radius` is bound. `center: Point { ... }` is "field `center`
   must fit this pattern". Literals inside a pattern are tests.
2. Any other circle. In a struct pattern, `..` means "ignore the remaining
   fields", here `center`.
3. A line: `x: x1` binds field `x` of the first point to the name `x1` (the
   field shorthand `{ x }` would bind it as `x`, and two points cannot both
   use that name). The **guard** `if x1 == x2` adds a condition that
   patterns cannot express, because a pattern cannot compare two parts of a
   value with each other.
4. Any other line. In a tuple-variant pattern, `(..)` ignores all fields.

Order matters as always: arm 2 also fits a centred circle, so arm 1 must come
first.

Matching on a **reference**, such as `&Order`, works too. Since the 2018
edition, Rust adjusts automatically: the pattern is written as if for the
value, and the bound names become references (`items` is then a
`&Vec<String>`). This is called **default binding modes**, and it is why
you rarely need to write `&` in patterns.

## let-else

A common shape in a function: take something apart, or give up. With `if
let` or `match`, the rest of the function ends up nested inside:

```rust
fn port_of(addr: &str) -> Option<u16> {
    if let Some((_, port)) = addr.rsplit_once(':') {
        port.parse().ok()
    } else {
        None
    }
}
```

`let ... else` flattens it. The pattern binds names for the **rest** of the
function, and the `else` block runs when it does not fit:

```rust
fn port_of(addr: &str) -> Option<u16> {
    let Some((_, port)) = addr.rsplit_once(':') else {
        return None;
    };
    port.parse().ok()
}
```

(`rsplit_once(':')` splits at the **last** `:`, giving `Some((before,
after))`, or `None` if there is none; `split_once` splits at the first.)

A plain `let` only accepts irrefutable patterns, which is why the `else` is
needed. Without it:

```text
error[E0005]: refutable pattern in local binding
  |
2 |     let Some((_, port)) = addr.rsplit_once(':');
  |         ^^^^^^^^^^^^^^^ pattern `None` not covered
  |
  = note: `let` bindings require an "irrefutable pattern", like a `struct` or an `enum` with only one variant
help: you might want to use `let...else` to handle the variant that isn't matched
```

The `else` block must **diverge**: end in something that never continues to
the next line, such as `return`, `break`, `continue` or `panic!`. Otherwise
`port` would not exist on the line after, and the compiler would have
nothing to give it:

```text
error[E0308]: `else` clause of `let...else` does not diverge
  |
2 |       let Some((_, port)) = addr.rsplit_once(':') else {
  |  ______________________________________________________^
3 | |         println!("no port");
4 | |     };
  | |_____^ expected `!`, found `()`
  |
  = help: try adding a diverging expression, such as `return` or `panic!(..)`
```

(`!` is the **never** type, the type of an expression that never finishes,
such as `return`.)

## matches! and if-let chains

`matches!(value, pattern)` is `true` when the value fits the pattern
(Beginner lesson 7), and accepts guards too:

```rust
let is_vowel = matches!(c, 'a' | 'e' | 'i' | 'o' | 'u');
let small_even = matches!(n, 0..=10 if n % 2 == 0);
```

**If-let chains** combine `if let` patterns and ordinary conditions with
`&&`, each part able to use names bound by the parts before it:

```rust
if let Some(user) = find(id)
    && user.active
{
    greet(user);
}
```

(A fragment.) This is new in the 2024 edition, which this course uses;
before it, the same needed an `if` nested inside an `if let`. (`||` is not
allowed in a chain: if either side could be true, which names would be
bound?)

## Irrefutable patterns are everywhere

Every `let` uses a pattern, as do function parameters and `for` loops:

```rust
let (a, b) = pair;                              // destructure a tuple
fn dist(&(x, y): &(f64, f64)) -> f64 { ... }    // destructure a parameter
for (i, item) in items.iter().enumerate() { }   // destructure each pair
```

(Fragments.) These must be irrefutable, since there is no "other arm" to go
to.

## Run it

```rust
fn summary(xs: &[i32]) -> String {
    match xs {
        [] => "empty".into(),
        [x] => format!("just {x}"),
        [first, second] => format!("{first} and {second}"),
        [first, .., last] => format!("{first} ... {last}"),
    }
}

fn sum(xs: &[i32]) -> i32 {
    match xs {
        [] => 0,
        [head, rest @ ..] => head + sum(rest),
    }
}

fn port_kind(port: u16) -> String {
    match port {
        p @ 1..=1023 => format!("privileged port {p}"),
        p @ 1024..=49151 => format!("registered port {p}"),
        p => format!("dynamic port {p}"),
    }
}

fn port_of(addr: &str) -> Option<u16> {
    let Some((_, port)) = addr.rsplit_once(':') else {
        return None;
    };
    port.parse().ok()
}

fn main() {
    let cases: [&[i32]; 4] = [&[], &[1], &[1, 2], &[1, 2, 3, 4]];
    for xs in cases {
        println!("{}", summary(xs));
    }
    println!("{}", sum(&[1, 2, 3, 4]));
    for p in [80, 8080, 60000] {
        println!("{}", port_kind(p));
    }
    println!("{:?} {:?} {:?}", port_of("localhost:8080"), port_of("localhost"), port_of("h:x"));

    let vowels: String = "education".chars().filter(|&c| matches!(c, 'a' | 'e' | 'i' | 'o' | 'u')).collect();
    println!("{vowels}");

    if let Some(n) = "42".parse::<i32>().ok()
        && n > 40
    {
        println!("big {n}");
    }
}
```

```output
empty
just 1
1 and 2
1 ... 4
10
privileged port 80
registered port 8080
dynamic port 60000
Some(8080) None None
euaio
big 42
```

`port_of("localhost")` returned at the `else`, since there is no `:`;
`port_of("h:x")` got past the `let`, and then `"x".parse()` failed, which
`.ok()` turned into `None`.

## Your turn

In `src/lib.rs`, using the pattern named in each item:

- `describe_slice(items: &[&str])`, with slice patterns: `"nothing"` for an
  empty slice, `"only a"` for `["a"]`, and otherwise first and last item plus
  the count: `"a to b (2 items)"`, `"a to c (3 items)"`
- `classify_age(age: u32)`, with `@`: `"newborn"` for 0, `"child"` for 1 to
  12, `"teenager aged 15"` for 13 to 19 (with the actual age), `"adult"` for
  20 and above
- `parse_kv(line)`, with `let-else`: split `"key = value"` at the **first**
  `=` and return both sides trimmed, borrowed from `line`:
  - `"name = Ana"` gives `Some(("name", "Ana"))`
  - `"url=http://x?a=b"` gives `Some(("url", "http://x?a=b"))`: later `=`
    signs belong to the value
  - `"empty ="` gives `Some(("empty", ""))`: an empty value is fine
  - no `=` at all, or a key that is empty after trimming (`"  = value"`),
    gives `None`
- `sum_pairs(values: &[i32])`, with `[a, b, rest @ ..]` and recursion: add
  neighbours in pairs; an odd item left at the end stays as it is:
  `[1, 2, 3, 4, 5]` gives `[3, 7, 5]`, `[]` gives `[]`
- `total_shipping(orders)`, with nested patterns on `Order` and
  `Destination`: the sum over all orders, where an order costs
  - 0 if it has no items, whatever its destination (check this first)
  - 15 for `Domestic { express: true }`, 5 for other domestic orders
  - 20 for `International` to `"SG"`, 30 for any other country

  (A `String` field cannot be compared with a literal in a pattern, so the
  country check is a guard: `... { country } if country == "SG"`.)
