---
title: Encoding is not encryption
summary: Base64, hex and XOR are reversible without a secret - and breaking a single-byte XOR "cipher" by hand shows why.
order: 1
files: [codes.py]
run: python codes.py
hints:
  - "`xor_bytes(data, key)`: XOR each byte of data with the key byte that lines up, cycling the key with `key[i % len(key)]`. Return bytes."
  - "XOR is its own inverse: the same function both scrambles and unscrambles, which is the whole point of the next task."
  - "`break_single_byte_xor(data)`: try every key from 0 to 255, XOR the data with it, and keep the result that looks like English text. Score by counting spaces and ASCII letters."
  - "`looks_like_text`: a decode is plausible when almost every byte is printable and it contains spaces - real sentences have spaces roughly every 5-6 characters."
---

People constantly mistake **encoding** for **encryption**. They are not the
same, and the difference is the single most common security misunderstanding
there is.

- **Encoding** rearranges data into a format that survives transport - base64,
  hex, URL-encoding. It is reversed with no secret at all. Its purpose is
  compatibility, never confidentiality.
- **Encryption** transforms data so that reversing it requires a **key**.
  Without the key it is infeasible to reverse.

When you see base64 "protecting" a token, a cookie or a config value, it is
protecting nothing. `base64.b64decode` is the entire attack.

## XOR: the bridge, and a trap

XOR is the one operation underneath almost all symmetric encryption, and on its
own it is also a classic trap. Combining each byte of data with a key byte:

```python
cipher = data ^ key
data   = cipher ^ key      # XOR undoes itself with the same key
```

With a long, random, never-reused key this is unbreakable - it is the one-time
pad. With a **single-byte** key it is a toy, and people still ship it believing
"it looks encrypted". It is not, because there are only 256 possible keys.

## Breaking it by hand

Try all 256 keys, decode with each, and recognise which result is real English.
That recognition - "this decode has spaces and letters, that one is noise" - is
a tool you will reach for again and again, because so much of attacking weak
crypto is *telling the right answer from 255 wrong ones*.

That is the lesson: a cipher whose entire key space can be tried in a
microsecond is not protection. The size of the key space is what matters, and
"it looks scrambled" tells you nothing about it.

## Your turn

In `codes.py`:

- `xor_bytes(data, key)` - XOR `data` (bytes) with `key` (bytes), repeating the
  key as needed; returns bytes. The same function encrypts and decrypts.
- `looks_like_text(data)` - `True` when `data` (bytes) is plausibly an English
  sentence: almost all printable, and containing at least one space
- `break_single_byte_xor(data)` - given bytes that were XORed with one repeated
  key byte, return the `(key, plaintext_str)` that decodes to real text
