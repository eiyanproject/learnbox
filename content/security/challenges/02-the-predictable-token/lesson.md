---
title: "Challenge: the predictable token"
summary: A server hands out session tokens from a seeded generator. You hold one. Recover the admin's.
order: 2
files: [recover.py]
run: python recover.py
hints:
  - "The server seeds `random.Random` with a value between 1000 and 2000 and issues `getrandbits(32)` tokens in order. Brute-force the seed that reproduces your token at your position."
  - "Once you know the seed, the admin's token is simply the first one that seed produces."
---

A web application issues session tokens with Python's `random` seeded from a
value in a small range - the mistake from the Cryptography randomness lesson,
in the wild. Tokens are handed out **in order** as users arrive. The admin
logged in first and got token #1; you arrived third and got token #3.

## The brief

You know:

- the server seeds `random.Random` with an integer in `[1000, 2000]`
- it issues `getrandbits(32)` values in arrival order
- your token (#3) is `MY_TOKEN` in `data.py`

Recover the **admin's** token (#1). Because the seed space is tiny and the
generator is reproducible, you can find the seed that reproduces your token at
position 3, then replay the sequence from the start. This is why `secrets`
exists and `random` must never issue anything an attacker should not guess.

## Your turn

In `recover.py`, write `recover_admin_token(my_token, my_position, lo=1000, hi=2000)`
returning the admin's token (#1), or `None` if no seed from `lo` to `hi` -
both included - reproduces `my_token` at position `my_position` (counting from
1).
