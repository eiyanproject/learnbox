---
title: "Capstone: a concurrent TCP server"
summary: A key-value server on std::net with a worker pool, shared state behind RwLock, a line protocol, and graceful shutdown.
order: 10
files: [src/lib.rs]
run: cargo test
hints:
  - "`Server::start`: `TcpListener::bind((host, port))?`, read the real port with `local_addr()?.port()`, `set_nonblocking(false)`, and move the listener into an accept thread."
  - "Shutdown: keep an `Arc<AtomicBool>`; the accept loop checks it after each connection, and `stop()` sets it and then dials the listener once (`TcpStream::connect`) so a blocking `accept` wakes up."
  - "Per connection: `BufReader::new(stream.try_clone()?)` for reading lines and the original stream for writing, so both directions work; end the loop when `read_line` returns 0."
  - "State is `Arc<RwLock<HashMap<String, String>>>`: `GET` takes `read()`, `SET`/`DEL` take `write()`. Never hold the guard while writing to the socket."
---

Everything from the Advanced and Pro tracks comes together: threads, channels,
shared state, traits, error handling and I/O, in about 150 lines.

## The shape

```text
TcpListener ──accept──▶ worker pool ──▶ handle_client(stream)
                                          read line ─▶ execute ─▶ write reply
                                                          │
                                            Arc<RwLock<HashMap>> shared state
```

## Binding and accepting

```rust
use std::net::{TcpListener, TcpStream};

let listener = TcpListener::bind(("127.0.0.1", 0))?;   // port 0: the OS picks a free port
let port = listener.local_addr()?.port();

for stream in listener.incoming() {
    let stream = stream?;
    pool.execute(move || handle_client(stream));
}
```

`incoming()` blocks in `accept`. A thread per connection is simple and fine for
a handful of clients; a **pool** bounds the number of threads (the same pool
you built in Advanced: Channels).

## Reading a line protocol

```rust
let mut reader = BufReader::new(stream.try_clone()?);
let mut line = String::new();
loop {
    line.clear();
    if reader.read_line(&mut line)? == 0 {
        break;                       // the client closed the connection
    }
    let reply = execute(line.trim());
    writeln!(stream, "{reply}")?;    // the original stream is the writer
}
```

`try_clone` gives a second handle to the same socket, so one can be buffered for
reading while the other writes.

## Shared state

`Arc<RwLock<HashMap<String, String>>>`: many readers at once, one writer.
Take the lock, do the map operation, drop the guard, **then** touch the socket.
Holding a lock across I/O is how a server stalls.

## Graceful shutdown

A blocking `accept` does not notice a flag. The portable trick is to set the
flag and then make one connection to your own listener, which wakes `accept`;
the loop sees the flag and returns.

That is only half of it. A worker blocked in `read_line` on a client that is
still connected never returns either, so joining the pool would hang. Keep a
list of the accepted streams (`try_clone` each one) and, during shutdown, call
`shutdown(Shutdown::Both)` on them: the reads return 0, the handlers finish,
and the pool joins cleanly.

## Errors on a per-connection basis

One client sending nonsense must not stop the server. Handle each connection in
its own function returning `io::Result<()>`, and log failures rather than
propagating them to the accept loop.

## Your turn

In `src/lib.rs`, build `Server`:

- `Server::new()` with an empty store; `start(host, port) -> io::Result<u16>`
  returning the bound port (pass `0` to get a free one); `stop()`
- protocol, one command per line, replies ending in `\n`:
  - `SET key value` (the value may contain spaces) replies `OK`
  - `GET key` replies the value or `NIL`
  - `DEL key` replies `1` or `0`
  - `KEYS` replies all keys sorted and space-separated
  - `PING` replies `PONG`; `QUIT` replies `BYE` and closes the connection
  - anything else replies `ERR unknown command`
- several clients at once, served by a pool of worker threads (at least 16, since
  a connection occupies its worker until the client disconnects)
- `store_len()` for tests, and a `stop()` that ends every thread even while a
  client is still connected
