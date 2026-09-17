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

## The core traits

`std::io` is built on a few traits, so the same code works on files, network
sockets, in-memory buffers and stdin/stdout:

- `Read`: `read(&mut buf)` pulls bytes. Implemented by `File`, `TcpStream`, `&[u8]`, `Stdin`.
- `Write`: `write(&buf)` and `flush()`. Implemented by `File`, `TcpStream`, `Vec<u8>`, `Stdout`.
- `BufRead`: a `Read` with an internal buffer, adding `read_line` and `lines()`.

Almost every I/O function returns `io::Result<T>`, so `?` is everywhere.

## Be generic over readers and writers

Write your logic against the traits, not against `File`:

```rust
use std::io::{self, BufRead, Write};

fn longest_line<R: BufRead>(reader: R) -> io::Result<String> {
    let mut best = String::new();
    for line in reader.lines() {
        let line = line?;
        if line.len() > best.len() { best = line; }
    }
    Ok(best)
}
```

In production you pass `BufReader::new(File::open(path)?)` or `stdin().lock()`.
In tests you pass `"a\nbbb\n".as_bytes()` (a `&[u8]` is a `BufRead`) and never
touch the disk. Writers work the same way with a `Vec<u8>`:

```rust
let mut out = Vec::new();
writeln!(out, "hello")?;
assert_eq!(out, b"hello\n");
```

## Buffering matters

`File` performs a system call per `read`/`write`. Reading line by line or
writing many small pieces without a buffer is dramatically slower. Wrap them:

```rust
use std::fs::File;
use std::io::{BufReader, BufWriter};

let reader = BufReader::new(File::open("in.txt")?);
let mut writer = BufWriter::new(File::create("out.txt")?);
```

A `BufWriter` flushes when dropped, but errors during that final flush are
lost; call `flush()` yourself to see them.

## Files and paths

```rust
use std::fs::{self, File, OpenOptions};
use std::path::{Path, PathBuf};

fs::read_to_string("config.toml")?;      // whole file, small files only
fs::write("out.txt", contents)?;
File::create(path)?;                     // create or truncate
OpenOptions::new().append(true).create(true).open(path)?;
fs::create_dir_all("data/cache")?;
let p = Path::new("data").join("scores.csv");
p.extension(); p.file_stem(); p.exists();
```

Functions that take paths usually accept `impl AsRef<Path>` (see Conversions).

## Custom errors

`io::Error::new(io::ErrorKind::InvalidData, "bad row 3")` makes an `io::Error`
for data problems, so a function can keep returning `io::Result`.

## Your turn

In `src/lib.rs`:

- `count_lines_and_words(reader)`: for any `BufRead`
- `write_report(out, rows)`: for any `Write`, one line per row: the name
  left-aligned in 10 columns, the value right-aligned in 5; then flush
- `sum_column(path, column)`: sum a numeric column of a CSV file with a header
  row; a non-numeric value is an `InvalidData` error mentioning the line number
- `append_log(path, line)`: append a line, creating the file if needed
- `copy_upper(src, dst)`: stream `src` to `dst` upper-cased, buffered both ways,
  returning the number of bytes written
