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

`asyncio` streams give you a TCP server in a few lines, and one event loop can
serve thousands of idle connections that would each need a thread otherwise.

## A server

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

`start_server` calls `handle` in a **new task for every connection**, so one
slow client does not block the others.

## A client

```python
reader, writer = await asyncio.open_connection("127.0.0.1", 9000)
writer.write(b"hello\n")
await writer.drain()
reply = await reader.readline()
```

Try it by hand: run the server, then in a second terminal
`printf 'SET a 1\nGET a\n' | nc 127.0.0.1 7070` (or `python -c` with sockets).

## Designing a line protocol

A text protocol with one request per line is easy to debug and easy to test:

- **Framing**: messages end with `\n`; `readline()` does the splitting.
- **Parsing**: `line.decode().strip().split(maxsplit=2)` keeps spaces inside
  the last argument (a value).
- **Errors are replies**, not crashes: a bad command answers `ERR ...` and the
  connection stays usable.
- **Bound the input**: a client sending a 10 GB line should not take the server
  down; `StreamReader` has a line limit (64 KiB by default).

## Shared state

All connection tasks run on one thread, and switch only at `await`, so a plain
dict shared by every connection is safe **as long as no `await` sits in the
middle of a read-modify-write**. That property is the big simplification
asyncio offers over threads.

## Shutting down

`server.close()` stops accepting, `await server.wait_closed()` waits for the
listener to close, and cancelling the per-connection tasks ends open sessions.
Test servers bind port `0` to get a free port from the OS.

## Your turn

In `kvserver.py`, complete `KVServer`:

- `handle_client(reader, writer)` speaks this protocol, one command per line:
  - `SET key value` stores (value may contain spaces), replies `OK`
  - `GET key` replies the value or `NIL`
  - `DEL key` replies `1` if it existed, else `0`
  - `KEYS` replies all keys sorted, space-separated (empty line if none)
  - `QUIT` replies `BYE` and closes the connection
  - anything else replies `ERR unknown command`
- `start(host="127.0.0.1", port=0)` starts listening and returns the actual port
- `stop()` closes the server

All connections share one store.
