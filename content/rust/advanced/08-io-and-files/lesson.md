---
title: I/O and files
summary: The Read, Write and BufRead traits, writing functions generic over any reader or writer, files and paths, and streaming large input line by line.
order: 8
files: [src/lib.rs]
run: cargo test
hints:
  - "`count_lines_and_words<R: BufRead>(reader: R) -> io::Result<(usize, usize)>`: `for line in reader.lines() { let line = line?; lines += 1; words += line.split_whitespace().count(); }`."
  - "`write_report<W: Write>(mut out: W, rows: &[(&str, u32)]) -> io::Result<()>`: `writeln!(out, \"{name:<10}{value:>5}\")?` per row, then `out.flush()`."
  - "`sum_column(path, column)`: `let file = File::open(path)?; let reader = BufReader::new(file);` then skip the header with `.lines().skip(1)` and `split(',').nth(column)`. Parse errors become `io::Error::new(io::ErrorKind::InvalidData, ...)`."
  - "`append_log(path, line)`: `OpenOptions::new().create(true).append(true).open(path)?` and `writeln!`. `copy_upper`: read with `BufReader`, write with `BufWriter`, and `flush` at the end."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **I/O** | input and output: files, the terminal, network connections, memory buffers |
| **`io::Result<T>`** | `Result<T, io::Error>`: nearly every I/O call can fail |
| **system call** | a request to the operating system; slow, so fewer and larger is better |
| **`Read`** / **`Write`** | the traits for reading bytes / writing bytes |
| **`BufRead`** | a buffered reader that can read lines |
| **reader** / **writer** | anything implementing `Read` / `Write`: a file, `stdin`, a `&[u8]`, a `Vec<u8>` |
| **generic over readers** | functions written against the traits, so tests can pass bytes instead of files |
| **byte string** | `b"hello\n"`: a `&[u8; N]` literal |
| **buffering** | reading or writing a large block at once (8 KiB by default) |
| **flush** | send a writer's buffered bytes out now; call it so errors are reported |
| **streaming** | processing input a piece at a time, so memory stays constant |
| **truncate** | `File::create` empties an existing file |
| **append** | add to the end of a file |
| **`io::ErrorKind`** | why an operation failed: `NotFound`, `PermissionDenied`, `InvalidData`... |
| **`Path`** / **`PathBuf`** | a borrowed / an owned path; not always valid UTF-8 |
| **CSV** | comma-separated values, here with a header line |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `use std::io::{self, BufRead, BufReader, BufWriter, Read, Write};` | brings in `io` and the traits |
| `use std::fs::{self, File, OpenOptions};` | files |
| `fn count<R: BufRead>(reader: R)`, `reader.lines()` | any buffered reader; its lines as `io::Result<String>` |
| `"a\nbbb\n".as_bytes()` | bytes in memory used as a reader |
| `fn write_report<W: Write>(mut out: W, ...)` | any writer |
| `writeln!(out, "{:<10}{:>5}", name, value)?` | left-align in 10, right-align in 5 |
| `out.flush()?` | writes out what is buffered |
| `BufReader::new(File::open(path)?)`, `BufWriter::new(File::create(path)?)` | buffered file reader / writer |
| `OpenOptions::new().append(true).create(true).open(path)?` | open for appending, creating if needed |
| `fs::read_to_string(path)?` | a whole small file |
| `err.kind() == io::ErrorKind::NotFound` | checks why it failed |
| `io::Error::new(io::ErrorKind::InvalidData, format!("bad row {n}"))` | your own I/O error |
| `Path::new("data").join("scores.csv")`, `p.extension()`, `p.display()` | build, inspect and print paths |
| `path: impl AsRef<Path>` | accepts any kind of path |
| `line.to_uppercase()`, `line.split(',').nth(column)` | upper case; one CSV column |

### Errors

| Error | Means |
|---|---|
| `error[E0599]: no method named lines found ... trait BufRead ... is not in scope` | import the trait |
| `cannot write into Vec<_>` | `write!` without `use std::io::Write` |
| `NotFound`, `InvalidData` | a missing file; malformed contents |

---

A program that cannot read input or save output is not much use. This
lesson covers **I/O** (input and output) in Rust: files, but also anything
else that bytes flow in and out of, such as the terminal, network
connections, or a buffer in memory. The central idea is that all of these
look the same to your code, through a few traits, so a function written for
"any reader" works on a file, the terminal, or a test string alike.

Two facts shape everything below:

- **I/O can always fail**: the file is missing, the disk is full, the network
  drops. So nearly every I/O function returns `io::Result<T>`, which is
  `Result<T, io::Error>`, and `?` appears on almost every line.
- **I/O is slow** compared to everything else a program does, mainly
  because each read or write goes through the operating system, a
  **system call**. Doing fewer, larger operations makes a large difference,
  which is what buffering is for.

## The core traits

`std::io` is built on three traits:

| Trait | Means | Key methods | Implemented by |
|---|---|---|---|
| `Read` | bytes can be pulled from it | `read(&mut buf)`, `read_to_string` | `File`, `TcpStream`, `Stdin`, `&[u8]` |
| `Write` | bytes can be pushed into it | `write_all(&buf)`, `flush()` | `File`, `TcpStream`, `Stdout`, `Vec<u8>` |
| `BufRead` | a `Read` with a buffer, which can find line ends | `read_line`, `lines()` | `BufReader<R>`, `StdinLock`, `&[u8]` |

Note the last column: a `&[u8]` (some bytes in memory) is a reader, and a
`Vec<u8>` is a writer. That is what lets I/O code be tested without files, below.

These are traits, so their methods only exist where the trait is imported.
Forget `use std::io::BufRead;` and the compiler says so, and names the trait:

```text
error[E0599]: no method named `lines` found for reference `&[u8]` in the current scope
 --> src/lib.rs:3:7
  |
3 |     r.lines().count()
  |       ^^^^^ method not found in `&[u8]`
  |
  = help: items from traits can only be used if the trait is in scope
help: trait `BufRead` which provides `lines` is implemented but not in scope; perhaps you want to import it
  |
1 + use std::io::BufRead;
```

The `write!` and `writeln!` macros need `std::io::Write` in the same way, and
without it report ``cannot write into `Vec<_>` ``.

## Be generic over readers and writers

Write your logic against the traits, not against `File`:

```rust
use std::io::{self, BufRead, Write};

fn longest_line<R: BufRead>(reader: R) -> io::Result<String> {
    let mut best = String::new();
    for line in reader.lines() {
        let line = line?;
        if line.len() > best.len() {
            best = line;
        }
    }
    Ok(best)
}
```

(A fragment.) `use std::io::{self, ...}` imports the module itself as `io`, so
`io::Result` works, along with the traits. `reader.lines()` yields one
`io::Result<String>` per line, since reading each line can fail; `let line =
line?;` unwraps it. The returned lines have their line ending (`\n` or
`\r\n`) removed. A last line without a final newline still counts.

The caller decides where the bytes come from:

- in the program: `longest_line(BufReader::new(File::open(path)?))`, or
  `longest_line(io::stdin().lock())` for the terminal;
- in a test: `longest_line("a\nbbb\n".as_bytes())`, with no file at all.

Writers work the same way. Writing into a `Vec<u8>` collects the bytes, ready
to compare:

```rust
let mut out = Vec::new();
writeln!(out, "hello")?;
assert_eq!(out, b"hello\n");
```

(A fragment.) `b"hello\n"` is a **byte string** literal, a `&[u8; 6]`. A
function taking `W: Write` by value can be passed `&mut out` too, since
`&mut W` is also a `Write`: that is how the exercise's test passes its
`Vec` to `write_report` and reads it afterwards. A writer parameter that is
written to must be `mut`: `fn write_report<W: Write>(mut out: W, ...)`.

## Buffering matters

A `File` turns every `read` or `write` call into a system call. Reading a
file line by line straight from a `File` would mean a system call for every
few bytes; writing a report one small `write!` at a time, the same.
**Buffered** wrappers fix that by reading or writing a large block (8 KiB by
default) at once, and serving your small calls from memory:

```rust
use std::fs::File;
use std::io::{BufReader, BufWriter};

let reader = BufReader::new(File::open("in.txt")?);         // also gives BufRead: lines()
let mut writer = BufWriter::new(File::create("out.txt")?);
```

(A fragment.) For many small operations, the difference is often ten times
or more. `BufReader` is also what you need for line-by-line reading, since a
plain `File` is only `Read`, not `BufRead`.

A `BufWriter` holds unwritten bytes in memory until its buffer fills or it
is **flushed**. When it is dropped, it flushes itself, but if that final
write fails (a full disk), the error has nowhere to go and is lost. Call
`writer.flush()?` yourself at the end, so a failure is reported.

**Streaming**, processing input a line or a block at a time instead of
reading it all into one `String` first, keeps memory use constant however
large the file is. `fs::read_to_string` is fine for small files such as
configuration; for data files of unknown size, stream.

## Files and paths

```rust
use std::fs::{self, File, OpenOptions};
use std::path::{Path, PathBuf};

fs::read_to_string("config.toml")?;      // the whole file as a String
fs::write("out.txt", contents)?;         // create or replace, in one call
File::open(path)?;                       // open for reading
File::create(path)?;                     // create, or empty an existing file!
OpenOptions::new().append(true).create(true).open(path)?;   // add to the end
fs::create_dir_all("data/cache")?;       // a folder and any missing parents
let p = Path::new("data").join("scores.csv");
p.extension();  p.file_stem();  p.exists();
```

(Fragments.) Notes on each:

- `File::create` **truncates**: an existing file is emptied first. To add to
  a log, open it with `OpenOptions`: `append(true)` makes every write go to
  the end, and `create(true)` creates the file if it does not exist yet.
- When a file cannot be opened, the `io::Error` has a **kind** that says why:
  `err.kind()` is `io::ErrorKind::NotFound`, `PermissionDenied`, and so on.
  Code can react to that, and the exercise's tests check for `NotFound`.
- `Path` is to `PathBuf` as `&str` is to `String`: a borrowed path, and an
  owned one. `join` adds a component with the right separator for the
  operating system. `display()` prints a path. Paths are not always valid
  UTF-8, which is why they are separate types from strings.
- Functions that take a path usually accept `impl AsRef<Path>` (lesson 6),
  so `"notes.txt"`, a `String`, a `&Path` and a `PathBuf` all work. The
  exercise's signatures do this.

## Your own I/O errors

When the *bytes* were read fine but their *content* is wrong, such as a
number column containing `lots`, you can still report it as an `io::Error`,
so the function keeps one error type:

```rust
io::Error::new(io::ErrorKind::InvalidData, format!("line {n}: not a number: {value}"))
```

(An expression.) `InvalidData` is the kind for "the data is malformed". The
message is what `to_string()` and `{}` print.

## Run it

```rust
use std::io::{self, BufRead, Write};
use std::path::Path;

fn longest_line<R: BufRead>(reader: R) -> io::Result<String> {
    let mut best = String::new();
    for line in reader.lines() {
        let line = line?;
        if line.len() > best.len() {
            best = line;
        }
    }
    Ok(best)
}

fn main() -> io::Result<()> {
    println!("{}", longest_line("a\nbbb\ncc\n".as_bytes())?);   // no file needed

    let mut out = Vec::new();
    writeln!(out, "hello")?;
    println!("{:?} {}", out, out == b"hello\n");

    let p = Path::new("data").join("scores.csv");
    println!("{} {:?} {:?}", p.display(), p.extension(), p.file_stem());

    let err = io::Error::new(io::ErrorKind::InvalidData, "bad row 3");
    println!("{:?}: {err}", err.kind());
    Ok(())
}
```

```output
bbb
[104, 101, 108, 108, 111, 10] true
data/scores.csv Some("csv") Some("scores")
InvalidData: bad row 3
```

`main` returns `io::Result<()>`, so `?` works in it (Intermediate lesson 2).
The `Vec<u8>` holds the bytes of `hello` and the newline, 10. The path parts
are `Option`s, because a path need not have an extension.

## Your turn

In `src/lib.rs`:

- `count_lines_and_words(reader)`, for any `BufRead`: the number of lines and
  of whitespace-separated words. An empty line counts as a line with no
  words, and a last line without a newline still counts:
  `"one two\n\nthree  four five\n"` is `(3, 5)`, `"no newline"` is `(1, 2)`,
  `""` is `(0, 0)`.
- `write_report(out, rows)`, for any `Write`: one line per row, the name
  left-aligned in 10 columns and the value right-aligned in 5 (`{:<10}` and
  `{:>5}`), so `("apples", 12)` is `"apples       12\n"`; then `flush()`
- `sum_column(path, column)`: the sum, as `f64`, of column number `column`
  (from 0) of a comma-separated file whose first line is a header:
  - skip the header, and skip empty lines
  - values may be whole or decimal: `90`, `82.5`
  - a value that does not parse is an error of kind `InvalidData` whose
    message contains `line <n>`, counting the file's lines from 1 with the
    header as line 1 (so the third line of the file is `line 3`)
  - a missing file is the `NotFound` error from `File::open`, passed up with
    `?`
- `append_log(path, line)`: add `line` and a newline to the end of the file,
  creating it if needed; calling it twice gives `"started\nstopped\n"`
- `copy_upper(src, dst)`: copy `src` to `dst` with every letter upper-cased,
  through a `BufReader` and a `BufWriter`, streaming rather than reading the
  whole file at once; return the number of bytes written and flush at the end
