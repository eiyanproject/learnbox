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
