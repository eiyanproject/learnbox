---
title: Borrowing and slices
summary: Use a value without taking it; one writer or many readers; views into strings and arrays.
order: 5
files: [src/lib.rs]
run: cargo test
hints:
  - "`first_word`: loop over `s.char_indices()`; at the first `' '` return `&s[..i]`. If there is no space, return `s` itself."
  - "`sum` takes `&[i32]`. `for n in nums { total += n; }` works because adding a `&i32` to an `i32` is allowed, or write `*n`."
  - "`double_all` takes `&mut [i32]`: `for n in nums.iter_mut() { *n *= 2; }`. The `*` writes through the reference."
  - "`append_greeting(buf: &mut String, name: &str)`: `buf.push_str(\"Hello, \"); buf.push_str(name); buf.push('\\n');`"
---

Moving a value into every function that wants to look at it would be
tiresome. Instead, you **borrow** it with a reference.

## References

```rust
fn length(s: &String) -> usize {
    s.len()
}

let name = String::from("Ana");
let n = length(&name);    // lend it
println!("{name}");       // still ours
```

`&name` creates a reference; the function gets to use the value but not own
it. When the function returns, nothing is dropped.

## Mutable references

To let a function change a value, lend it mutably:

```rust
fn add_bang(s: &mut String) {
    s.push('!');
}

let mut msg = String::from("hi");
add_bang(&mut msg);       // msg is now "hi!"
```

## The borrowing rule

At any moment you can have **either**:

- any number of shared references `&T`, **or**
- exactly one mutable reference `&mut T`

but not both. This is checked at compile time and rules out a whole class of
bugs, such as changing a vector while something else is reading it:

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];
v.push(4);                // error: cannot borrow `v` as mutable
println!("{first}");      // because `first` is still in use here
```

`push` might move the vector's buffer, which would leave `first` pointing at
freed memory. The compiler refuses.

A borrow lasts until its **last use**, not until the end of the block. Move
the `println!` above the `push` and the code compiles.

## Dereferencing

`*` follows a reference to the value behind it:

```rust
let mut x = 5;
let r = &mut x;
*r += 1;                  // x is now 6
```

Method calls and most operators dereference automatically, which is why you
rarely see `*` except when writing through `&mut`.

## Slices

A slice is a reference to part of a sequence.

```rust
let s = String::from("hello world");
let hello: &str = &s[0..5];
let world: &str = &s[6..];

let nums = [10, 20, 30, 40];
let middle: &[i32] = &nums[1..3];    // [20, 30]
```

`&str` is a string slice. That is why functions should take `&str` rather than
`&String`: a `&String`, a string literal and a slice of either all work.
Likewise, take `&[T]` rather than `&Vec<T>`.

String slice positions are **bytes**. Slicing in the middle of a multi-byte
character panics, so find positions with `char_indices()` or `find()` rather
than guessing.

## Your turn

In `src/lib.rs`:

- `first_word(s)`: the text up to the first space, as a slice of `s` (no new
  `String`). No space means the whole string.
- `sum(nums)`: the sum of a slice of `i32`
- `double_all(nums)`: double every number **in place**
- `append_greeting(buf, name)`: add the line `Hello, <name>` and a newline to
  the end of `buf`
