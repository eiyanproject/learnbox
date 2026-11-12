---
title: "Capstone: a concurrent TCP server"
summary: A key-value server on std::net with a worker pool, shared state behind RwLock, a line protocol, and graceful shutdown.
order: 10
files: [src/lib.rs]
run: cargo test
hints:
  - "`Server::start`: `TcpListener::bind((host, port))?`, read the real port with `local_addr()?.port()`, and move the listener into an accept thread."
  - "Shutdown: keep an `Arc<AtomicBool>`; the accept loop checks it after each connection, and `stop()` sets it and then dials the listener once (`TcpStream::connect`) so a blocking `accept` wakes up."
  - "Per connection: `BufReader::new(stream.try_clone()?)` for reading lines and the original stream for writing, so both directions work; end the loop when `read_line` returns 0."
  - "State is `Arc<RwLock<HashMap<String, String>>>`: `GET` takes `read()`, `SET`/`DEL` take `write()`. Never hold the guard while writing to the socket."
---

This capstone brings the Advanced and Pro tracks together in one program
of about 150 lines: a small **key-value server**, a simplified version of
what Redis or memcached do. Clients connect over TCP, send one command per
line (`SET name Ana`, `GET name`), and get one reply per line. It uses
threads and a worker pool (Advanced lessons 1 and 2), shared state behind a
lock (Advanced lesson 3), atomics (Pro lesson 4), buffered I/O (Advanced
lesson 8), and an API that is safe to start and stop.

## Background: TCP in one paragraph

**TCP** is the protocol most of the internet uses for reliable, ordered
byte streams between two programs. A server **listens** on a **port** (a
number from 1 to 65535 on its machine); a client **connects** to that host
and port; from then on each side has a **stream** it can read from and write
to, like a file, until one side closes it. TCP carries bytes, not messages,
so the two sides agree on a **protocol** for where one message ends: here,
each command and each reply is one line ending in `\n`. In Rust,
`std::net::TcpListener` is the listening side, and `TcpStream` a connection;
`TcpStream` implements `Read` and `Write`, so everything from the I/O lesson
applies.

## The shape

```text
                       ┌─────────────── worker pool (16 threads) ─────────────┐
 TcpListener ─accept─> │ handle_client(stream):                               │
 (accept thread)       │   loop: read a line -> execute -> write the reply    │
                       └──────────────────────────────┬───────────────────────┘
                                                      │
                                   Arc<RwLock<HashMap<String, String>>>
                                   the store, shared by every connection
```

One thread **accepts** new connections and hands each to the pool. Each
worker serves one connection at a time, reading commands until the client
leaves. The store is shared by all of them.

## Binding and accepting

```rust
use std::net::{TcpListener, TcpStream};

let listener = TcpListener::bind(("127.0.0.1", 0))?;   // port 0: the OS picks a free port
let port = listener.local_addr()?.port();              // which one it picked

for stream in listener.incoming() {
    let stream = stream?;
    pool.execute(move || handle_client(stream));
}
```

(A fragment.) `bind` takes anything that can be turned into an address,
such as a `(host, port)` tuple. Asking for port 0 lets the operating system
choose a free one, which is how the tests run many servers without
clashing; `local_addr()` then reports the real port, which `start` must
return. `incoming()` is an iterator whose `next` **blocks** in `accept`
until a client connects, then yields that connection.

A thread per connection is simple and fine for a handful of clients. A
**pool** puts a ceiling on the number of threads, the same pool you built in
Advanced lesson 2. Since each connection keeps its worker busy until the
client disconnects, the pool needs at least as many workers as clients you
expect at once; the tests use 8 at the same time, and ask for at least 16.

## Reading a line protocol

```rust
let mut reader = BufReader::new(stream.try_clone()?);
let mut line = String::new();
loop {
    line.clear();
    if reader.read_line(&mut line)? == 0 {
        break;                       // 0 bytes: the client closed the connection
    }
    let reply = execute(line.trim());
    writeln!(stream, "{reply}")?;    // the original stream is the writer
}
```

(A fragment.) Three details:

- `stream.try_clone()` gives a **second handle to the same connection**.
  One goes into a `BufReader` (for `read_line`), the other is used to write.
  A single handle cannot be inside a `BufReader` and be written to at the
  same time, since the `BufReader` owns or borrows it.
- `read_line` returns how many bytes it read, and **0 means end of stream**:
  the client has closed its side. That ends the loop and the handler.
- `line.clear()` reuses one buffer for every command (lesson 5).

## The commands, separate from the socket

Keep the protocol logic in a function that knows nothing about sockets: a
line goes in, a reply comes out. Then it can be tested directly, as the
exercise's tests do with `execute(&store, "SET a 1")`, and the network code
is only plumbing. The same idea, a handler generic over any `BufRead` and
`Write` (Advanced lesson 8), lets a whole conversation run in memory:

```rust
use std::io::{self, BufRead, Write};

fn reply_to(line: &str) -> (String, bool) {
    match line.trim().to_uppercase().as_str() {
        "PING" => ("PONG".to_string(), false),
        "QUIT" => ("BYE".to_string(), true),
        _ => ("ERR unknown command".to_string(), false),
    }
}

fn serve<R: BufRead, W: Write>(mut input: R, mut output: W) -> io::Result<usize> {
    let mut line = String::new();
    let mut handled = 0;
    loop {
        line.clear();
        if input.read_line(&mut line)? == 0 {
            break;
        }
        handled += 1;
        let (reply, close) = reply_to(&line);
        writeln!(output, "{reply}")?;
        if close {
            break;
        }
    }
    Ok(handled)
}

fn main() -> io::Result<()> {
    let mut out = Vec::new();
    let handled = serve("ping\nFLY\nQUIT\nPING\n".as_bytes(), &mut out)?;
    print!("{}", String::from_utf8(out).unwrap());
    println!("{handled} lines handled");
    Ok(())
}
```

```output
PONG
ERR unknown command
BYE
3 lines handled
```

The command was matched case-insensitively (`ping`), the unknown one got an
error reply and the conversation continued, and `QUIT` ended it, so the last
`PING` was never read. A real `TcpStream` pair plugs into `serve` unchanged.

## Shared state

The store is `Arc<RwLock<HashMap<String, String>>>` (Advanced lesson 3):
`GET` and `KEYS` take the read lock, so many clients can read at once; `SET`
and `DEL` take the write lock. Take the lock, do the map operation, **drop
the guard**, and only then write to the socket.

Holding a lock across I/O is how servers stall. Writing to a socket can
block for as long as the client takes to read, and a slow or stuck client
would then freeze every other connection waiting for the lock. Computing
the reply as a `String` first, as `execute` does, makes the separation
natural: the guard is dropped when `execute` returns.

## Graceful shutdown

`stop()` must end every thread the server started, and close the listener so
the port is free again (the tests check that connecting afterwards fails).
That is harder than it sounds, because two kinds of thread are blocked in
calls that do not look at any flag:

1. **The accept thread** is blocked in `accept`. The portable trick: set an
   `AtomicBool` "stopping" flag, then **connect to your own listener once**.
   That wakes `accept`, the loop checks the flag, sees it set, and returns,
   dropping the listener, which closes the port.
2. **Workers serving connected clients** are blocked in `read_line`, and
   would wait until those clients leave, so joining the pool would hang.
   Keep a list of the accepted streams (a `try_clone` of each, in a
   `Mutex<Vec<TcpStream>>`), and during shutdown call
   `stream.shutdown(Shutdown::Both)` on each: their reads return 0, the
   handlers finish, and the pool's workers can be joined.

`stop()` must also be safe to call twice, and dropping a `Server` that was
never stopped should stop it: implement `Drop` to call it.

## Errors per connection

One client sending nonsense, or disconnecting halfway through a reply, must
not stop the server. Handle each connection in its own function returning
`io::Result<()>`, and when it returns an error, log or ignore it inside the
worker; never let it reach the accept loop or panic the worker.

## Your turn

In `src/lib.rs`, build `Server`:

- `Server::new()` with an empty store
- `start(&mut self, host, port) -> io::Result<u16>`: bind, start the accept
  thread and the pool (at least 16 workers), and return the port actually
  bound (with `0`, the one the system chose)
- `execute(store, line) -> (reply, should_close)`, one command per line.
  Command names are case-insensitive (`get a` works); keys and values are
  case-sensitive. Split the line on single spaces into at most three parts:
  - `SET key value` replies `OK`; the value is everything after the key and
    may contain spaces (`SET name Ana Wijaya`)
  - `GET key` replies the value, or `NIL` if there is none
  - `DEL key` replies `1` if the key existed, `0` if not
  - `KEYS` replies all keys sorted and separated by single spaces
  - `PING` replies `PONG`
  - `QUIT` replies `BYE`, and `should_close` is `true`: after sending the
    reply the server closes the connection
  - anything else, including the right command with the wrong number of
    arguments (`GET` alone) and an empty line, replies `ERR unknown command`
    and keeps the connection open
- each reply is sent as one line ending in `\n`
- several clients at once: the tests run 8 clients concurrently, each making
  25 `SET`s, and expect all 200 keys in the store
- `store_len()` (given) for the tests
- `stop()`, ending every thread even while a client is still connected,
  closing the listener so the port no longer accepts connections, and safe
  to call more than once
