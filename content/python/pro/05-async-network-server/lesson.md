---
title: An async network server
summary: Build a TCP key-value server with asyncio streams, a line protocol, per-connection tasks and graceful shutdown.
order: 5
files: [kvserver.py]
run: python kvserver.py
hints:
  - "`handle_client(reader, writer)`: `while line := await reader.readline():` decode and `split(maxsplit=2)`, compute a reply, then `writer.write((reply + \"\\n\").encode())` and `await writer.drain()`. Close in `finally`: `writer.close(); await writer.wait_closed()`."
  - "Dispatch on the command: `SET k v` stores and replies `OK`, `GET k` replies the value or `NIL`, `DEL k` replies `1` or `0`, `KEYS` replies the sorted keys joined by spaces, anything else `ERR unknown command`."
  - "`QUIT` replies `BYE` and then breaks out of the loop so the connection closes."
  - "`start(host, port)`: `server = await asyncio.start_server(self.handle_client, host, port)`; the real port is `server.sockets[0].getsockname()[1]` when you pass port 0."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **network server** | a program that waits for other programs to connect and answers them |
| **client** | a program that connects to a server |
| **key-value store** | a store of values looked up by key, like Redis or memcached |
| **TCP** | the standard way two programs exchange an ordered stream of bytes over a network |
| **listen** | wait for incoming connections on an address and port |
| **address** | where a machine is; `127.0.0.1` means "this machine only" |
| **port** | a number from 1 to 65535 identifying one listening program; `0` asks for any free one |
| **socket** | the operating system's handle for one network endpoint |
| **stream** (`StreamReader`, `StreamWriter`) | asyncio's objects for receiving and sending a connection's bytes |
| **peer name** | the client's own address and port |
| **bytes literal** | `b"hello\n"`: raw bytes, not text |
| **encode** / **decode** | text to bytes / bytes to text, UTF-8 by default |
| **back-pressure** | waiting for the send buffer to drain, so a slow reader cannot fill the server's memory |
| **protocol** | the agreed format of the messages |
| **framing** | marking where one message ends; here each message ends with `\n` |
| **line protocol** | a text protocol with one request per line |
| **parsing** | splitting a message into its parts |
| **netcat** (`nc`) | a terminal tool that sends and receives raw network data |
| **graceful shutdown** | stopping new connections, then ending open ones cleanly |
| **NIL** | this protocol's reply for "no such key" |

### Python names and functions

| Name | What it does |
|---|---|
| `asyncio.start_server(handler, host, port)` | listens, calling `handler(reader, writer)` in a new task for each connection |
| `server.serve_forever()`, `async with server:` | keeps it running; closes it at the end of the block |
| `server.sockets[0].getsockname()[1]` | the port the server actually got |
| `server.close()`, `await server.wait_closed()` | stop accepting connections; wait for the listening socket to close |
| `await reader.readline()` | the next whole line as bytes; `b""` when the client has closed |
| `writer.write(data)`, `await writer.drain()` | queue bytes to send; wait until the queue has room |
| `writer.close()`, `await writer.wait_closed()` | close the connection; wait until it is closed |
| `writer.get_extra_info("peername")` | the client's address and port |
| `asyncio.open_connection(host, port)` | connects, giving a reader and a writer |
| `line.decode().strip().split(maxsplit=2)` | text, trimmed, split on spaces at most twice |
| `socket.create_connection((host, port))`, `s.sendall(b)`, `s.recv(n)` | a plain socket client: connect; send; receive up to `n` bytes |
| `" ".join(sorted(store))` | the keys sorted, separated by spaces |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python kvserver.py` | starts the server on port 7070 |
| `printf 'SET a 1\nGET a\n' \| nc 127.0.0.1 7070` | sends two commands with netcat |
| `python -c "..."` | runs a one-line Python program, here a small client |
| Ctrl+C | stops the server |

---

This lesson puts the asyncio lesson to work on a real job: a small network
server, of the same shape as Redis or memcached, that stores keys and values
and answers commands from many clients at once. Network servers are where
asyncio shines. Most clients are idle most of the time, waiting to send
their next command, and one event loop can serve thousands of idle
connections that would each need a thread otherwise.

A few terms first. **TCP** is the standard way two programs talk over a
network: once connected, each side can send a stream of bytes, and TCP
delivers them in order. A server **listens** on an **address** (`127.0.0.1`
means "this machine only") and a **port** (a number from 1 to 65535 that
identifies one listening program on that machine). Clients **connect** to
that address and port.

## A server

asyncio's **streams** wrap a TCP connection in two objects: a
`StreamReader` to receive bytes, and a `StreamWriter` to send them. This
server sends every line it receives back in capitals:

```python
import asyncio

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    try:
        while line := await reader.readline():      # b"" means the client closed
            writer.write(line.upper())
            await writer.drain()                    # respect back-pressure
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 9000)
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

Line by line:

- `start_server(handle, host, port)` starts listening and returns a
  `Server`. Each time a client connects, it calls `handle` with that
  connection's reader and writer. `serve_forever()` keeps it running.
- `peername` is the client's own address and port, handy for logging.
- `await reader.readline()` waits, without blocking anyone else, until a
  whole line (ending in `\n`) has arrived, and returns it as **bytes**. When
  the client closes the connection it returns `b""`, which is falsy, so the
  `while` loop ends.
- `writer.write(...)` queues bytes to send. `await writer.drain()` waits
  until the queue has room again. Without it, a client that reads slowly
  could make the server buffer unlimited data in memory; waiting for the
  buffer to drain is called respecting **back-pressure**.
- The `finally` block closes the connection however the loop ends, even if
  the handler raises.

`start_server` calls `handle` in a **new task for every connection**, so one
slow client does not block the others: while one handler waits at
`readline()`, the loop runs the rest.

Network data is bytes, not text. `b"hello\n"` is a bytes literal, and you
convert between the two with `.encode()` (text to bytes) and `.decode()`
(bytes to text), which use UTF-8 by default.

## A client

The client side is the mirror image. `open_connection` connects and gives
you a reader and a writer:

```python
reader, writer = await asyncio.open_connection("127.0.0.1", 9000)
writer.write(b"hello\n")
await writer.drain()
reply = await reader.readline()
```

Here is the whole round trip in one runnable piece. Passing port `0` asks
the operating system for any free port, and the server's socket then reports
which one it got:

```pycon
>>> import asyncio
>>> async def shout(reader, writer):
...     while line := await reader.readline():
...         writer.write(line.upper())
...         await writer.drain()
...     writer.close()
...
>>> async def demo():
...     server = await asyncio.start_server(shout, "127.0.0.1", 0)
...     port = server.sockets[0].getsockname()[1]
...     reader, writer = await asyncio.open_connection("127.0.0.1", port)
...     writer.write(b"hello\n")
...     await writer.drain()
...     reply = await reader.readline()
...     writer.close()
...     server.close()
...     await server.wait_closed()
...     return reply
...
>>> asyncio.run(demo())
b'HELLO\n'
```

To try your own server by hand, press **Run** to start it (it listens on port
7070), then in a second terminal tab send it some commands. If `nc`
(netcat) is installed, `printf 'SET a 1\nGET a\n' | nc 127.0.0.1 7070` does it;
otherwise this Python one-liner does the same:

```console
$ python -c "import socket, time; s = socket.create_connection(('127.0.0.1', 7070)); s.sendall(b'SET a 1\nGET a\n'); time.sleep(0.2); print(s.recv(100).decode())"
OK
1
```

(The short `sleep` gives the server time to answer both commands before the
one-liner reads.)

Stop the server with Ctrl+C.

## Designing a line protocol

A **protocol** is the agreed format of the messages. A text protocol with
one request per line is easy to debug (you can read it, and type it by hand)
and easy to test:

- **Framing**: the receiver needs to know where one message ends and the next
  begins, because TCP delivers a stream of bytes with no message boundaries
  of its own. Here messages end with `\n`, and `readline()` does the
  splitting.
- **Parsing**: `line.decode().strip().split(maxsplit=2)` splits on spaces at
  most twice, so the third part keeps any spaces inside it. That is how
  `SET name Ana Wijaya` gives `["SET", "name", "Ana Wijaya"]`, with the whole
  value in one piece.
- **Errors are replies**, not crashes: a bad command answers `ERR ...` and the
  connection stays usable. A handler that raised on bad input would drop the
  client's connection over a typo.
- **Bound the input**: a client sending a 10 GB line should not take the
  server down by filling its memory. `StreamReader` has a line limit (64 KiB
  by default) and raises an error for longer lines instead of buffering them.

```pycon
>>> "SET name Ana Wijaya\n".strip().split(maxsplit=2)
['SET', 'name', 'Ana Wijaya']
>>> "GET name\n".strip().split(maxsplit=2)
['GET', 'name']
>>> "KEYS\n".strip().split(maxsplit=2)
['KEYS']
```

The number of parts tells you whether a command has the arguments it needs:
`GET` needs exactly two parts, `SET` three, `KEYS` one.

## Shared state

All connection tasks run on one thread, and switch only at `await`, so a
plain dict shared by every connection is safe **as long as no `await` sits in
the middle of a read-modify-write**. `self.store[key] = value` runs from
start to finish without any other task getting a turn, so no lock is needed.
If you wrote `old = store[k]`, then `await` something, then `store[k] = old +
1`, another task could change `store[k]` during the `await`, the same race as
with threads. That property, that you can see every place a switch can
happen, is the big simplification asyncio offers over threads.

## Shutting down

`server.close()` stops accepting new connections, and
`await server.wait_closed()` waits for the listening socket to close.
Connections that are already open have their own handler tasks; cancelling
those tasks ends the open sessions.

Tests bind port `0`, as the demo above did, to get a free port from the
operating system: a fixed port might already be taken by another program, or
by a previous test run that has not quite let go of it.

## Your turn

In `kvserver.py`, complete `KVServer` (the starter's `main()` runs it on
port 7070 when you press **Run**):

- `handle_client(reader, writer)` speaks this protocol, one command per line,
  replying with one line each:
  - `SET key value` stores the value (which may contain spaces), replies `OK`
  - `GET key` replies the value, or `NIL` if there is no such key
  - `DEL key` deletes the key and replies `1` if it existed, else `0`
  - `KEYS` replies all keys sorted, separated by single spaces (an empty
    line if there are none)
  - `QUIT` replies `BYE` and closes the connection
  - anything else, including a known command with the wrong number of
    arguments such as a bare `GET`, replies `ERR unknown command` and keeps
    the connection open
- `start(host="127.0.0.1", port=0)` starts listening and returns the actual
  port number as an `int` (which matters when `port` is `0`).
- `stop()` closes the server.

All connections share one store, `self.store`, so a value set by one client
can be read by another. A test connects ten clients at once, each setting 20
keys, so connections must be served concurrently.
