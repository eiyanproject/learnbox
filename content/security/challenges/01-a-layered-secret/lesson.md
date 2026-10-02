---
title: "Challenge: a layered secret"
summary: A flag wrapped in three reversible layers. No key was used - only the belief that scrambling is protection.
order: 1
files: [solve.py]
run: python solve.py
hints:
  - "The layers, outermost first: base64, then a one-byte XOR, then the text was reversed. Undo them in that order."
  - "No XOR key is given - but a single byte has only 256 possibilities, and the real flag starts with 'flag{'."
---

A flag was hidden by stacking three reversible transformations, and whoever did
it believed the result was safe because it looked like noise. Every layer here
is something from the Foundations and Cryptography sections, and none of them
needs a secret to undo.

## The brief

`BLOB` in `data.py` was produced like this, from a flag of the form
`flag{...}`:

1. the flag text was **reversed**
2. the result was **XORed** with a single, unknown byte
3. that was **base64-encoded**

Recover the original flag. The XOR key was not recorded - but it is one byte, so
there are only 256 to try, and only one of them produces readable text beginning
`flag{`. This is the whole lesson of the first two sections in one problem:
encoding is not encryption, and a one-byte key is no key at all.

## Your turn

In `solve.py`, write `crack(blob)` returning the recovered flag string.
