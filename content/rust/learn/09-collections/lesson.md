---
title: Vec, String and HashMap
summary: The three collections you will use in almost every Rust program.
order: 9
files: [src/lib.rs]
run: cargo test
hints:
  - "`word_counts`: `*counts.entry(word.to_lowercase()).or_insert(0) += 1;` inside `for word in text.split_whitespace()`."
  - "`dedup_sorted(mut v: Vec<i32>)`: `v.sort(); v.dedup(); v`."
  - "`group_by_length`: `groups.entry(word.len()).or_insert_with(Vec::new).push(word.to_string());`."
  - "`reverse_words`: `text.split_whitespace().rev().collect::<Vec<_>>().join(\" \")`."
---

## Vec

A growable list of values of one type:

```rust
let mut v: Vec<i32> = Vec::new();
v.push(3);
v.push(1);
let w = vec![3, 1, 4, 1, 5];     // vec! macro with initial values

w[0]            // 3, panics if out of range
w.get(10)       // Option<&i32>: None instead of a panic
w.len()
w.contains(&4)
v.pop()         // Option<i32>, removes the last item

for n in &w { }        // borrow each item
for n in &mut v { *n += 1; }   // change each item
```

Sorting and friends change the vector in place:

```rust
let mut nums = vec![3, 1, 3, 2];
nums.sort();          // [1, 2, 3, 3]
nums.dedup();         // [1, 2, 3]   removes consecutive duplicates
nums.reverse();
```

## String

`String` is a growable UTF-8 buffer. `&str` borrows from one.

```rust
let mut s = String::from("hello");
s.push(' ');
s.push_str("world");
let t = s.clone() + "!";        // + takes ownership of the left side
let u = format!("{s}, again");  // format! borrows everything: usually clearer

s.len()                  // bytes, not characters
s.chars().count()        // characters
s.to_uppercase()
s.contains("wor")
s.replace("world", "rust")
s.split(',')             // an iterator of &str
s.split_whitespace()
s.trim()
```

You cannot index a string with `s[0]`: in UTF-8 a character can take one to
four bytes, so "the first character" is not a byte position. Use
`s.chars().next()`.

## HashMap

```rust
use std::collections::HashMap;

let mut ages: HashMap<String, u32> = HashMap::new();
ages.insert("Ana".to_string(), 31);
ages.get("Ana")              // Option<&u32>
ages.contains_key("Budi")
ages.remove("Ana");

for (name, age) in &ages {
    println!("{name}: {age}");
}
```

Iteration order is **not** stable. Sort the keys if you need an order.

## The entry API

"Look up this key; if it is missing, insert a default; then change it" is so
common it has its own API:

```rust
let mut counts: HashMap<&str, usize> = HashMap::new();
for word in ["a", "b", "a"] {
    *counts.entry(word).or_insert(0) += 1;
}
// {"a": 2, "b": 1}
```

`or_insert` returns a `&mut` to the value, hence the `*` to add to it.
`or_insert_with(Vec::new)` builds the default only when needed.

## Your turn

In `src/lib.rs`:

- `word_counts(text)`: how many times each word appears, lower-cased, words
  separated by whitespace
- `dedup_sorted(v)`: the numbers sorted with duplicates removed
- `group_by_length(words)`: word length to the words of that length, in the
  order they appear
- `reverse_words(text)`: the words in reverse order, joined by single spaces
