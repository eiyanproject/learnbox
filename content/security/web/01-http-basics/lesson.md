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

Every web attack - injection, forgery, traversal, all of it - is at bottom a
**request the server did not expect**. A browser builds ordinary requests for
you, which is exactly why you have to be able to build them yourself: the
interesting ones are the ones a browser never would.

## A request

```text
GET /search?q=cat HTTP/1.1
Host: example.com
User-Agent: curl/8.0
Cookie: session=abc123

```

- A **request line**: method, path, protocol version.
- **Headers**, `Name: value`, one per line - metadata about the request.
- A blank line, then an optional **body** (where `POST` data goes).

On the wire every line ends with `\r\n` - a carriage return then a line feed,
not just the `\n` you are used to - so the blank line is a bare `\r\n` and the
**head** (request line plus headers) is separated from the body by `\r\n\r\n`.

The methods that matter: `GET` reads, `POST` submits, and the rest (`PUT`,
`DELETE`, `HEAD`) round it out. The security-relevant point is that the method,
path, headers and body are all **attacker-controlled** - every one of them is a
place to put something unexpected.

## A response

```text
HTTP/1.1 200 OK
Content-Type: text/html
Set-Cookie: session=abc123

<html>...
```

A status line (`200` ok, `301/302` redirect, `403` forbidden, `404` missing,
`500` error), headers, blank line, body. The status code is the first thing you
read when probing: a `200` where you expected `403` is a finding.

## Why by hand

Tools like `curl` and the browser's dev tools send and show raw requests, and
every proxy you will use works at this level. Reimplementing the parse and build
is how the structure stops being magic - after this, "set the `Cookie` header"
or "this endpoint trusts the `X-Forwarded-For` header" is something you can see
and do directly.

## Your turn

In `http_tools.py`:

- `parse_request(raw)` - a dict with the keys `method`, `path`, `version`,
  `headers` and `body`. `headers` is a dict whose names are lower-cased and
  whose values have surrounding spaces stripped; `body` is everything after the
  blank line, or `""` when there is nothing
- `build_response(status, headers, body)` - the raw response text: the status
  line `HTTP/1.1 <status>` (e.g. `status="200 OK"`), one `Name: value` line per
  header in `headers`, a blank line, then `body` - every line ending in `\r\n`
- `query_params(path)` - the `?k=v&k=v` part of a path as a dict of strings
  (empty when there is none; a `k=` with nothing after it gives `""`, and no
  URL-decoding is needed)
