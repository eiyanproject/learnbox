---
title: The shape of an HTTP request
summary: Every web attack is a crafted request, so the first skill is reading and building the request and response by hand.
order: 1
files: [http_tools.py]
run: python http_tools.py
hints:
  - "`parse_request`: split the raw text on the blank line (`\r\n\r\n`) into head and body. The first line of the head is `METHOD PATH VERSION`; every line after it is `Name: value`."
  - "Header names are case-insensitive in HTTP; store them lower-cased so lookups are predictable."
  - "`build_response`: the status line is `HTTP/1.1 <status>`, then one `Name: value` line per header, then a blank line, then the body."
  - "`query_params`: split the path on `?`; the part after it is `k=v&k=v`. Return a dict, and handle a path with no query."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **HTTP** | the text protocol browsers and web servers talk; HTTPS is the same inside TLS |
| **client** | the program that sends a request: a browser, `curl`, a script |
| **server** | the program that answers it |
| **request** | what the client sends: a request line, headers, a blank line, an optional body |
| **response** | what the server sends back: a status line, headers, a blank line, a body |
| **request line** | the first line: method, path, version, such as `GET /search?q=cat HTTP/1.1` |
| **method** (verb) | what the client wants to do: `GET` reads, `POST` submits, `PUT` replaces, `DELETE` removes, `HEAD` gets only the headers |
| **path** | the part of the address after the host name: `/search?q=cat` |
| **query string** | the part of the path after `?`: `q=cat&safe=on`, pairs joined with `&` |
| **parameter** | one `name=value` pair in a query string or form body |
| **header** | one `Name: value` line of extra information, such as `Host` or `Cookie` |
| **head** | the request (or status) line plus the headers: everything before the blank line |
| **body** | everything after the blank line: form data, JSON, an HTML page |
| **CRLF** (`\r\n`) | carriage return then line feed: how every HTTP line ends |
| **status code** | the server's three-digit answer: `200` OK, `301`/`302` redirect, `403` forbidden, `404` not found, `500` server error |
| **case-insensitive** | `Host`, `host` and `HOST` mean the same header |
| **cookie** | a value the server asks the browser to send back with every request, often the session token |
| **`Set-Cookie`** | the response header that gives the browser a cookie |
| **attacker-controlled** | any part of a request: a client can put anything there, not only what a browser would |
| **proxy** | a tool that sits between browser and server and shows or changes the raw requests |
| **URL-decoding** | turning `%20` back into a space; not needed in this lesson |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `curl -v URL` | sends a request and shows both sides: `>` lines were sent, `<` lines received |
| `curl -H 'Name: value' URL` | adds or replaces a request header |
| `curl -d 'a=1&b=2' URL` | sends a `POST` with that body |
| `python http_tools.py` | runs your program: parses a request and its query string |

### Python names

| Name | What it does |
|---|---|
| `s.partition(sep)` | splits at the first `sep` into `(before, sep, after)`; `after` is `""` if there is no `sep` |
| `head, _, body = ...` | takes the three parts; `_` is the one not needed |
| `s.split("\r\n")` | the text cut into lines |
| `s.split(" ", 2)` | split on spaces, at most twice, so three parts |
| `lines[0]`, `lines[1:]` | the first line; all the others |
| `s.strip()` | the text without spaces at either end |
| `s.lower()` | the text in lowercase |
| `headers.items()` | each `(name, value)` pair of a dict |
| `"\r\n".join(lines)` | the lines joined, each separated by CRLF |
| `{}` | an empty dict |

---

Every web attack, whether injection, forgery or path traversal, comes down to
the same thing: **a request the server did not expect**. A browser builds
ordinary requests for you. That is exactly why you need to be able to read and
build them yourself: the interesting requests are the ones a browser would
never send.

## What a request looks like

HTTP is plain text. Here is what `curl -v` shows when it fetches a page from a
small local server: the lines starting with `>` are what it sent, the lines
starting with `<` what came back.

```text
> GET /index.html?q=cat HTTP/1.1
> Host: 127.0.0.1:8765
> User-Agent: curl/8.23.0
> Accept: */*
>
< HTTP/1.0 200 OK
< Server: SimpleHTTP/0.6 Python/3.14.8
< Content-type: text/html
< Content-Length: 3
<
hi
```

A request has four parts:

1. The **request line**: the **method** (`GET`), the **path**
   (`/index.html?q=cat`) and the protocol version (`HTTP/1.1`).
2. **Headers**, one `Name: value` per line: extra information, such as which
   site (`Host`), which program (`User-Agent`), and any **cookies**.
3. A blank line.
4. An optional **body**, where `POST` puts form data.

On the wire, every line ends with `\r\n` (carriage return, line feed), not just
the `\n` of an ordinary text file. So the blank line is a bare `\r\n`, and the
**head** (request line plus headers) is separated from the body by
`\r\n\r\n`. That one separator is what your parser splits on.

### The query string

The part of the path after `?` is the **query string**: **parameters** as
`name=value` pairs, joined with `&`. In `/search?q=cat&safe=on` there are two:
`q` is `cat` and `safe` is `on`. Search boxes, filters and page numbers usually
travel this way.

### The methods

| Method | Meaning |
|---|---|
| `GET` | read something; should never change anything |
| `POST` | submit something: a form, a login, an upload |
| `PUT`, `DELETE` | replace, remove |
| `HEAD` | like `GET`, but the headers only |

The point that matters for security: **every part of a request is
attacker-controlled**. The method, the path, every header and the body can
contain anything at all. A server that trusts a header just because a browser
would have sent a sensible value has a bug.

## What a response looks like

```text
HTTP/1.1 200 OK
Content-Type: text/html
Set-Cookie: session=abc123

<html>...
```

A status line, headers, a blank line, and the body. The **status code** is the
first thing to read when testing a site:

| Code | Meaning |
|---|---|
| `200` | OK |
| `301`, `302` | redirect: look at the `Location` header |
| `403` | forbidden: you are not allowed |
| `404` | not found |
| `500` | the server failed, often because of input it did not expect |

A `200` where you expected a `403` is a finding. So is a `500`: it means your
input reached somewhere it should not have.

`Set-Cookie` asks the browser to store a cookie and send it back, in a `Cookie`
header, with every later request. That is how a site remembers that you are
logged in.

## Why by hand

`curl` and the browser's developer tools show raw requests, and every
security **proxy** works at this level. Writing the parser and builder
yourself takes the mystery out. After this, "set the `Cookie` header" or "this
page trusts the `X-Forwarded-For` header" is something you can see and do
directly.

```pycon
>>> from http_tools import build_response
>>> build_response("404 Not Found", {"Content-Type": "text/plain"}, "nope")
'HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nnope'
```

## Your turn

In `http_tools.py`:

- `parse_request(raw)`: a dict with the keys `method`, `path`, `version`,
  `headers` and `body`.
  - `headers` is a dict whose names are lowercased and whose values have the
    spaces around them removed (header names are case-insensitive, so
    lowercase makes lookups reliable).
  - `body` is everything after the blank line, or `""` when there is none.
- `build_response(status, headers, body)`: the raw response text: the status
  line `HTTP/1.1 <status>` (for example `status="200 OK"`), one
  `Name: value` line per header, a blank line, then `body`, with every line
  ending in `\r\n`.
- `query_params(path)`: the `?k=v&k=v` part of a path as a dict of strings.
  It is empty when there is no `?`; a `k=` with nothing after it gives `""`;
  no URL-decoding is needed.

Run it:

```text
{'method': 'GET', 'path': '/search?q=cat&safe=on', 'version': 'HTTP/1.1', 'headers': {'host': 'example.com'}, 'body': ''}
{'q': 'cat', 'safe': 'on'}
```

## Check yourself

1. What separates the head of a request from its body?
   *A blank line: `\r\n\r\n` on the wire.*
2. Which parts of a request can an attacker change?
   *All of them: method, path, headers and body.*
3. What are the parameters in `/items?page=2&sort=`?
   *`page` is `"2"` and `sort` is `""`.*
4. Why store header names in lowercase?
   *They are case-insensitive, so `Host` and `host` are the same header.*
5. You expected `403` and got `200`. What does that mean?
   *The server let you do something it should have refused.*
