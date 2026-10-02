---
title: Stream ciphers and the nonce trap
summary: A keystream turns XOR into real encryption - until a nonce is reused, at which point the whole thing unravels.
order: 2
files: [stream.py]
run: python stream.py
hints:
  - "`keystream`: build bytes by hashing `key + nonce + counter` for counter 0, 1, 2... concatenating the digests, and cutting to `length`. Use `counter.to_bytes(8, 'big')`."
  - "`stream_xor`: XOR the data with `keystream(key, nonce, len(data))`. The same function encrypts and decrypts."
  - "`recover_xor_of_plaintexts`: just XOR the two ciphertexts together. If they used the same key and nonce, the keystream cancels and you are left with `p1 XOR p2`."
  - "`safe_encrypt`: make a fresh random nonce with `secrets.token_bytes(16)` every time, and return `(nonce, ciphertext)` so it can be decrypted."
---

In the foundations lesson, single-byte XOR was a toy because its key was tiny.
Make the key as long as the message, random, and never reused, and XOR becomes
the **one-time pad** - provably unbreakable. The problem is practical: you
cannot share a key as long as everything you will ever send.

A **stream cipher** solves that. From a short key and a **nonce** (a
number-used-once), it generates a long pseudo-random **keystream**, and XORs the
message with that. Here the keystream comes from hashing the key, nonce and a
counter - a real construction in spirit, close to how AES-CTR works.

```python
keystream = H(key, nonce, 0) || H(key, nonce, 1) || ...
ciphertext = plaintext XOR keystream
```

Decryption is the same operation: regenerate the identical keystream and XOR
again.

## The trap that destroys it

The security rests entirely on the keystream being used **once**. Encrypt two
messages with the same key *and the same nonce*, and both are XORed with the
identical keystream. Now watch what an attacker does with the two ciphertexts:

```text
c1 = p1 XOR K
c2 = p2 XOR K
c1 XOR c2 = p1 XOR p2     # the keystream K cancels out entirely
```

The key never appears. The attacker now has the XOR of the two plaintexts, and
with any knowledge of one - or just the statistics of the language - can often
peel both apart. This is the **two-time pad**, and it has broken real systems,
because reusing a nonce feels harmless and is total.

The defence is a rule with no exceptions: **a fresh, unique nonce for every
single encryption.** You will write both - the attack that recovers
`p1 XOR p2`, and the safe wrapper that generates a new nonce each time.

## Your turn

In `stream.py`:

- `keystream(key, nonce, length)` - `length` pseudo-random bytes from
  `key + nonce + counter`, as above
- `stream_xor(key, nonce, data)` - encrypt or decrypt `data` under `key` and
  `nonce`
- `recover_xor_of_plaintexts(c1, c2)` - given two ciphertexts made with the same
  key and nonce, return `p1 XOR p2`
- `safe_encrypt(key, data)` - encrypt with a fresh random nonce; return
  `(nonce, ciphertext)`
