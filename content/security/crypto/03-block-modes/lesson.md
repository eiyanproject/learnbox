---
title: Block cipher modes
summary: Why encrypting each block independently leaks the shape of your data, and how chaining with an IV hides it.
order: 3
files: [modes.py]
run: python modes.py
hints:
  - "`block_transform` is given to you - a stand-in for a real cipher. Use it as the per-block step; the lesson is about the mode around it, not the cipher."
  - "`ecb_encrypt`: split data into `bs`-byte blocks and transform each one on its own. Identical input blocks give identical output blocks - that is the leak."
  - "`has_repeated_blocks`: cut the ciphertext into `bs`-byte blocks and check whether any two are equal."
  - "`cbc_encrypt`: XOR each plaintext block with the previous ciphertext block (the first uses the IV) before transforming. Now identical plaintext blocks encrypt differently."
---

Real ciphers like AES work on fixed-size **blocks** - 16 bytes at a time. A
message longer than one block has to be split, and the **mode** is how the
blocks are put back together. The choice of mode is where a correct cipher is
routinely ruined.

## ECB: the one never to use

The obvious approach - encrypt each block on its own - is called **ECB**, and it
has a fatal property: identical plaintext blocks produce identical ciphertext
blocks. The cipher is intact, yet the *pattern* of the data shows straight
through. Encrypt an image in ECB and you can still see the picture, because
every region of one colour becomes the same repeated ciphertext block. Any
structure - repeated records, fixed headers, a padded field - leaks.

Detecting it is therefore easy: if a ciphertext has repeated blocks, it was
almost certainly ECB over repetitive data. That detector is your attack.

## CBC: chaining hides the pattern

The fix is to make each block depend on the one before it. **CBC** XORs each
plaintext block with the *previous ciphertext block* before encrypting, so
identical plaintext blocks no longer line up. The very first block has nothing
before it, so it is XORed with an **initialisation vector** (IV) - a random,
non-secret value.

For CBC, unique is **not** enough: the IV must be **unpredictable**. If an
attacker can predict the next IV and get their own plaintext encrypted, they can
craft a block that tests a guess at an earlier secret block - a match in the
ciphertext confirms the guess. That is how the BEAST attack broke TLS 1.0, which
used the previous message's last ciphertext block as the next IV. Generate every
CBC IV with `secrets.token_bytes`. (Counter-mode nonces, from the last lesson,
only need to be unique - a different rule for a different mode.)

```text
ECB:  c_i = E(p_i)                      same p_i  ->  same c_i   (leaks)
CBC:  c_i = E(p_i XOR c_{i-1})          same p_i  ->  different  (hidden)
```

To keep the focus on the mode, you are given a `block_transform` standing in for
a real block cipher. It is deliberately simple and is *not* secure on its own -
the point of the lesson is the structure around it, which is exactly what ECB
gets wrong and CBC gets right regardless of how strong the underlying cipher is.

## Your turn

In `modes.py` (all data is a whole number of `bs`-byte blocks):

- `ecb_encrypt(key, data, bs=16)` - transform each block independently
- `has_repeated_blocks(data, bs=16)` - `True` when any two `bs`-byte blocks are
  identical; your ECB detector
- `cbc_encrypt(key, iv, data, bs=16)` - chain each block with the previous
  ciphertext block, the first using `iv`
