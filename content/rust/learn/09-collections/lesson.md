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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **collection** | a growable container that keeps its contents on the heap |
| **`Vec<T>`** (vector) | a growable list of one type, in order |
| **`String`** | growable UTF-8 text that owns its bytes |
| **`&str`** | a borrowed view of text |
| **`HashMap<K, V>`** | values found by a key; each key at most once |
| **key** / **value** | what you look up by / what you find |
| **UTF-8** | the text encoding where a character takes 1 to 4 bytes |
| **index** | a position, from 0 |
| **out of bounds** | an index past the end; `v[i]` panics, `v.get(i)` gives `None` |
| **in place** | sorting and friends change the vector itself, so it must be `mut` |
| **consecutive duplicates** | equal items side by side; all `dedup` removes |
| **iterator** | something that produces items one at a time (Learn lesson 11) |
| **hash** | the number a key is turned into, deciding where it is stored |
| **iteration order** | a `HashMap` has none you can rely on; it can differ from run to run |
| **entry API** | `map.entry(key)`: find the slot, fill it if empty, update it in one step |
| **mutable reference** | what `or_insert` returns, so `*... += 1` changes the value in the map |
| **`use`** | brings a name into scope, such as `HashMap` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `Vec::new()`, `vec![1, 2, 3]` | an empty vector (type needed); one with items |
| `v.push(x)`, `v.pop()`, `v.len()`, `v.contains(&x)` | add; remove the last (an `Option`); length; membership |
| `v[i]`, `v.get(i)` | read by position: panics / `Option` |
| `v.sort()`, `v.dedup()`, `v.reverse()` | change the vector in place |
| `s.push_str("!")`, `s.clone() + "x"`, `format!(...)` | grow a `String`; join with `+`; build text |
| `s.to_lowercase()`, `s.len()`, `s.chars().count()` | lower case; bytes; characters |
| `s.split(' ')`, `s.split_whitespace()` | pieces; pieces between any whitespace |
| `.collect::<Vec<_>>()` | gathers an iterator into a vector |
| `s.chars().nth(0)`, `s.bytes().nth(0)` | a character; a byte, each as an `Option` |
| `words.join(" ")` | joins with single spaces |
| `use std::collections::HashMap;` | brings in `HashMap` |
| `map.insert(k, v)`, `map.get(&k)`, `map["k"]` | add; look up (`Option`); look up or panic |
| `*counts.entry(word).or_insert(0) += 1` | the counting idiom |
| `map.entry(k).or_insert_with(Vec::new).push(item)` | the grouping idiom |
| `map.into_iter()` | moves the pairs out, for example to sort them |

### Errors

| Error | Means |
|---|---|
| `index out of bounds: the len is 3 but the index is 10` | a panic from `v[10]` |
| `error[E0277]: the type str cannot be indexed by {integer}` | `s[0]` on a string; use `chars().nth` |
| `type annotations needed for Vec<_>` | `Vec::new()` with nothing to show the item type |

---

Arrays (lesson 2) have a length fixed when the program is compiled. Most real
data is not like that: you do not know in advance how many lines a file has
or how many words a user types. The standard library's **collections** keep
their contents on the heap (lesson 4) and grow as needed. Three of them cover
most needs:

| Collection | Holds | Use it for |
|---|---|---|
| `Vec<T>` | a list of `T`, in order | "these things, in this order" |
| `String` | UTF-8 text | any text you build or change |
| `HashMap<K, V>` | values of type `V`, each found by a key of type `K` | "look up X by Y" |

All three own their contents: when the collection is dropped, everything in
it is dropped too.

## Vec

A **vector** is a growable list of values of one type:

```rust
let mut v: Vec<i32> = Vec::new();   // empty; the type must be written
v.push(3);
v.push(1);
let w = vec![3, 1, 4, 1, 5];        // the vec! macro, with initial values
```

(A fragment.) `Vec::new()` starts empty, so the compiler cannot guess the
item type from it; the `: Vec<i32>` says it. With `vec![...]`, the items show
the type.

Reading and changing:

```rust
w[0]            // 3
w.get(0)        // Some(&3)
w.get(10)       // None
w.len()         // 5
w.contains(&4)  // true; contains takes a reference
v.pop()         // Some(1): removes and returns the last item, None if empty

for n in &w { }                 // borrow each item: n is &i32
for n in &mut v { *n += 1; }    // change each item in place
```

(Expressions with their values.) There are two ways to read by position,
and they differ in what happens when the position does not exist:

```rust
fn main() {
    let w = vec![1, 2, 3];
    let i = 10;
    println!("{:?}", w.get(i));    // None
    println!("{}", w[i]);          // panics
}
```

```text
None
thread 'main' (4242) panicked at src/main.rs:5:20:
index out of bounds: the len is 3 but the index is 10
```

`w[i]` panics: the program stops, rather than reading whatever memory lies
past the end, as C would. `w.get(i)` returns an `Option` (lesson 8) and lets
you decide. Use `[i]` when a wrong index would be a bug in your own code, and
`get` when the index comes from outside (user input, a file) and may really
be out of range.

Sorting and friends change the vector in place, so it must be `mut`:

```rust
let mut nums = vec![3, 1, 3, 2];
nums.sort();          // [1, 2, 3, 3]
nums.dedup();         // [1, 2, 3]
nums.reverse();       // [3, 2, 1]
```

`dedup` removes only **consecutive** duplicates: `[3, 1, 3]` stays as it is,
because the two 3s are not next to each other. That is why it is almost
always used after `sort`, which puts equal values side by side.

## String

A `String` is a growable piece of UTF-8 text that owns its bytes on the
heap. A `&str` (lesson 5) is a borrowed view of some text: a string literal,
or part of a `String`.

```rust
let mut s = String::from("hello");
s.push(' ');                    // add one char
s.push_str("world");            // add a &str
let t = s.clone() + "!";        // + takes ownership of the left side
let u = format!("{s}, again");  // format! only borrows: usually clearer
```

(A fragment.) `+` moves the `String` on its left and gives back a new one,
which is why `s.clone()` is written there: without it `s` would be moved and
unusable after that line. `format!` works like `println!` but returns the
text instead of printing it, and borrows everything, so it is the convenient
choice when combining several pieces.

Common methods, with `s` as `"hello world"`:

```rust
s.len()                  // 11: bytes, not characters
s.chars().count()        // 11: characters
s.to_uppercase()         // "HELLO WORLD", a new String
s.contains("wor")        // true
s.replace("world", "rust")   // "hello rust", a new String
s.split(',')             // the pieces between commas, as &str values
s.split_whitespace()     // the words, skipping any run of spaces, tabs, newlines
s.trim()                 // without whitespace at both ends, as a &str
```

(Expressions with their values.) `split` and `split_whitespace` give an
**iterator**, which produces the pieces one at a time; loop over it with
`for`, or gather it into a `Vec` with `.collect()` (iterators are lesson 11).
The difference matters for the exercise: `"a  b".split(' ')` gives `"a"`,
`""` and `"b"`, an empty piece between the two spaces, while
`split_whitespace` gives only `"a"` and `"b"`.

### Strings cannot be indexed

In Python or Java, `s[0]` is the first character. In Rust, it does not
compile:

```rust
let s = String::from("hi");
let c = s[0];
```

```text
error[E0277]: the type `str` cannot be indexed by `{integer}`
  |
2 |     let c = s[0];
  |               ^ string indices are ranges of `usize`
  |
  = help: the trait `SliceIndex<str>` is not implemented for `{integer}`
  = note: you can use `.chars().nth()` or `.bytes().nth()`
```

Why not? A `String` stores UTF-8 bytes, and in UTF-8 a character takes one to
four bytes: `h` is one byte, `é` two, `😀` four. So "character number 5" is
not at byte 5, and finding it means walking the string from the start.
Rust refuses to make that slow walk look like a fast `[i]`, and refuses to
hand you half a character. The `note:` names the two honest alternatives:

- `s.chars().nth(0)` walks the characters: `Some('h')`. (`.chars().next()`
  is the same for the first one.)
- `s.bytes().nth(0)` gives the raw byte: `Some(104)`.

Slicing with a range of byte positions, `&s[0..1]`, is allowed (lesson 5),
and panics if a position falls inside a character.

## HashMap

A `HashMap<K, V>` stores **key → value** pairs, and finds the value for a key
quickly however many pairs there are, where a `Vec` would have to look
through every item. Each key appears at most once. It is not in scope by
default, so it needs a `use`:

```rust
use std::collections::HashMap;

let mut ages: HashMap<String, u32> = HashMap::new();
ages.insert("Ana".to_string(), 31);     // add, or replace the old value
ages.get("Ana")                         // Some(&31)
ages.get("Budi")                        // None
ages.contains_key("Ana")                // true
ages.remove("Ana");                     // Some(31), and it is gone

for (name, age) in &ages {
    println!("{name}: {age}");
}
```

(A fragment.) `get` returns an `Option`, because the key may be missing.
`ages["Ana"]` also works, and panics when the key is missing, like `w[10]`.

Iteration order is **not** the order you inserted, and can differ from one
run of the program to the next. That is not a bug: the map stores pairs
where the key's hash points, and Rust deliberately varies the hashing per run
to resist attacks. If you need an order, collect the pairs into a `Vec` and
sort it, as the program below does. Tests usually compare a whole map with
`assert_eq!`, which does not care about order.

## The entry API

Counting things is the classic map job: for each word, if it is not in the
map yet, start it at 0; then add 1. Written with `get` and `insert`:

```rust
let mut counts: HashMap<&str, usize> = HashMap::new();
for word in ["a", "b", "a"] {
    let old = counts.get(word).copied().unwrap_or(0);
    counts.insert(word, old + 1);
}
```

That looks the key up twice and is easy to get subtly wrong. The **entry API**
does it in one step:

```rust
let mut counts: HashMap<&str, usize> = HashMap::new();
for word in ["a", "b", "a"] {
    *counts.entry(word).or_insert(0) += 1;
}
// {"a": 2, "b": 1}
```

Taking `*counts.entry(word).or_insert(0) += 1` apart:

1. `counts.entry(word)` finds the slot for `word`, filled or empty.
2. `.or_insert(0)` puts `0` there if it was empty, and in either case returns
   a `&mut usize`: a mutable reference to the value in the map.
3. `*... += 1` writes through that reference (lesson 5's `*`), changing the
   number inside the map.

To collect several values per key, make the value a `Vec`:
`map.entry(key).or_insert_with(Vec::new).push(item)`. `or_insert_with` takes
a function and calls it only when the key is missing, so no empty `Vec` is
built for keys that already have one.

## Run it

```rust
use std::collections::HashMap;

fn main() {
    let w = vec![3, 1, 4, 1, 5];
    println!("{} {:?} {} {}", w[0], w.get(10), w.len(), w.contains(&4));

    let mut nums = vec![3, 1, 3, 2];
    nums.sort();
    print!("{nums:?} ");
    nums.dedup();
    print!("{nums:?} ");
    nums.reverse();
    println!("{nums:?}");

    let mut s = String::from("hello");
    s.push(' ');
    s.push_str("world");
    let t = s.clone() + "!";
    println!("{t} | {} {}", "héllo".len(), "héllo".chars().count());
    println!("{:?} {:?}", s.chars().next(), s.bytes().next());
    println!("{:?}", "a  b".split(' ').collect::<Vec<_>>());
    println!("{:?}", "a  b".split_whitespace().collect::<Vec<_>>());

    let mut counts: HashMap<&str, usize> = HashMap::new();
    for word in ["a", "b", "a"] {
        *counts.entry(word).or_insert(0) += 1;
    }
    let mut pairs: Vec<_> = counts.into_iter().collect();
    pairs.sort();                       // a HashMap has no order of its own
    println!("{pairs:?}");
}
```

```output
3 None 5 true
[1, 2, 3, 3] [1, 2, 3] [3, 2, 1]
hello world! | 6 5
Some('h') Some(104)
["a", "", "b"]
["a", "b"]
[("a", 2), ("b", 1)]
```

`"héllo"` is 6 bytes but 5 characters, because `é` takes two bytes. 104 is
the byte for `h`. `counts.into_iter()` moves the pairs out of the map into a
`Vec` of tuples, which `sort` orders by the first item, then the second.

## Your turn

In `src/lib.rs`:

- `word_counts(text)`: how many times each word appears, as a
  `HashMap<String, usize>`. Words are separated by any amount of whitespace,
  and counting ignores case, with the keys stored in lower case:
  `"the cat The hat  THE bat"` gives `the` 3, `cat` 1, `hat` 1, `bat` 1. Text
  with no words gives an empty map.
- `dedup_sorted(v)`: the numbers sorted from smallest to largest, each one
  only once: `[3, 1, 3, 2, 1]` gives `[1, 2, 3]`
- `group_by_length(words)`: a map from word length (in bytes, `.len()`) to
  the words of that length, as `String`s, each list in the order the words
  appear: `["ant", "bee", "wasp", "fly", "moth"]` gives 3 → `["ant", "bee",
  "fly"]` and 4 → `["wasp", "moth"]`
- `reverse_words(text)`: the words in reverse order, joined by single spaces,
  however many spaces were between them: `"one two  three"` gives
  `"three two one"`, and `""` gives `""`
