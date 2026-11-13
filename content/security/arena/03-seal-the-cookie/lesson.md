---
title: "Round 3: Seal the cookie"
summary: A session cookie anyone can edit is not a session. Sign it, check it, and refuse everything that does not check out.
order: 3
files: [seal.py]
run: python -i seal.py
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 1300
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **session cookie** | the value a site stores in your browser to remember who you are |
| **base64** | a way to write bytes as text; anyone can decode it, so it hides nothing (Foundations lesson 1) |
| **URL-safe base64** | base64 using `-` and `_` instead of `+` and `/`, so it fits in a cookie or a URL |
| **JSON** | a text format for data, such as `{"user": "ana", "admin": false}` |
| **sorted keys** | the dict's keys written in alphabetical order, so the same data always gives the same text |
| **payload** | the data part of the token |
| **signature** | here, an HMAC of the payload: only someone with the key can make the right one |
| **HMAC-SHA256** | a keyed hash (Foundations lesson 2) |
| **seal** | add a signature so any change can be detected |
| **unseal** | check the signature and, only if it is right, read the data |
| **forged token** | one changed or made without the key |
| **expiry** (`exp`) | the time, in seconds, after which the token is no longer accepted |
| **`BadToken`**, **`Expired`** | the exceptions in `seal.py`; `Expired` is a kind of `BadToken` |
| **verify before parsing** | never hand unchecked data to a parser |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -i seal.py` | runs your file, then leaves Python open so you can try `seal` and `unseal` |

### Python names

| Name | What it does |
|---|---|
| `json.dumps(data, sort_keys=True)` | the dict as JSON text, keys sorted |
| `json.loads(text)` | JSON text back into Python data |
| `base64.urlsafe_b64encode(b)`, `base64.urlsafe_b64decode(s)` | URL-safe base64, both ways |
| `.encode()`, `.decode()` | text to bytes, bytes to text |
| `hmac.new(key, payload.encode(), "sha256").hexdigest()` | the signature, as hex |
| `hmac.compare_digest(a, b)` | compares in constant time |
| `token.split(".")` | the token cut at each dot |
| `isinstance(x, dict)` | `True` when `x` is a dict, a JSON object |
| `now >= data["exp"]` | the token has expired |
| `except ValueError:` | catches a decoding error so it can be turned into `BadToken` |

---

The site keeps `{"user": "ana", "admin": false}` in a cookie, as plain
base64. A support ticket this morning showed someone had changed `false` to
`true`. The cookie has to be sealed before the next release.

## The task

In `seal.py`, write `seal` and `unseal`. The two exception classes are
already there.

### `seal(data, key)`

`data` is a dict, `key` is `bytes`. Return a token string of two parts
joined by a dot:

```text
<payload>.<signature>
```

- **payload**: `data` as JSON with sorted keys
  (`json.dumps(data, sort_keys=True)`), UTF-8 encoded, then URL-safe base64
  (`base64.urlsafe_b64encode`), as text
- **signature**: the HMAC-SHA256 of the payload text under `key`, as hex
  (`hmac.new(key, payload.encode(), "sha256").hexdigest()`)

### `unseal(token, key, now)`

Check the token and return the dict. Raise `BadToken` when:

- the token does not have exactly two parts
- the signature is not the right one for that payload and key - a changed
  payload, a changed signature, an empty signature, the wrong key
- the payload is not base64 of a JSON object

Compare signatures with `hmac.compare_digest`, never `==`, and check the
signature **before** you decode anything: unverified data should not reach
the JSON parser.

If the dict has an `"exp"` key it is an expiry time, a number of seconds.
When `now` is greater than or equal to it, raise `Expired`, which is a kind
of `BadToken`. A token without `"exp"` does not expire.

```python
token = seal({"user": "ana", "exp": 1000}, b"secret")
unseal(token, b"secret", now=999)     # {"user": "ana", "exp": 1000}
unseal(token, b"secret", now=1000)    # raises Expired
unseal(token, b"other", now=999)      # raises BadToken
```

This is the defender's half only: the point is that a forged token is
refused, whatever was done to it.
