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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **challenge** | a problem with less guidance than a lesson: you decide how to solve it |
| **session token** | the value that proves you are logged in; whoever has it is that user |
| **seed** | the starting value of a pseudo-random generator; the same seed gives the same sequence (Crypto lesson 1) |
| **seed space** | every value the seed could have been; here 1000 to 2000 |
| **issued in order** | each new visitor gets the next number the generator produces |
| **position** | which number in the sequence a token was: first, second, third |
| **reproduce** | run the same generator from the same seed and get the same numbers |
| **brute force** | try every possible value, here every seed in the range |
| **inclusive range** | both ends count: `[1000, 2000]` includes 1000 and 2000 |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python recover.py` | runs your program: prints the admin's token |

### Python names

| Name | What it does |
|---|---|
| `MY_TOKEN` | given to you in `data.py`: your token, number 3 |
| `random.Random(seed)` | a generator of its own, started from `seed` |
| `.getrandbits(32)` | the generator's next 32-bit number |
| `range(lo, hi + 1)` | `lo` up to and including `hi` |
| `[r.getrandbits(32) for _ in range(n)]` | the first `n` numbers from `r` |
| `issued[-1]` | the last of them |
| `return None` | the way to say "no seed matched" |

---

A web application gives out session tokens using Python's `random`, seeded
with a number from a small range. It is the mistake from Crypto lesson 1,
found in the wild.

Tokens are given out **in order**, as users arrive. The admin logged in first
and got token number 1. You arrived third and got token number 3.

## The brief

You know three things:

- the server seeds `random.Random` with a whole number from 1000 to 2000;
- it gives out `getrandbits(32)` values in the order users arrive;
- your own token, number 3, is `MY_TOKEN` in `data.py`.

Recover the **admin's** token, number 1.

Two facts make this possible. The **seed space** is tiny: only 1,001 possible
seeds. And the generator is **reproducible**: the right seed, run again,
produces exactly the same tokens in the same order. Somewhere in that range is
the one seed whose third number is your token, and its first number is the
admin's.

The lesson behind the challenge: this is why `secrets` exists, and why
`random` must never produce anything an attacker should not be able to guess.

## Your turn

In `recover.py`, write
`recover_admin_token(my_token, my_position, lo=1000, hi=2000)`. It returns
the admin's token (number 1), or `None` if no seed from `lo` to `hi`, both
included, reproduces `my_token` at position `my_position` (counting from 1).

## Check yourself

1. Why does knowing the seed reveal every token?
   *The generator gives the same sequence from the same seed.*
2. How many seeds are there to try?
   *1,001: 1000 to 2000, both included.*
3. What should the server have used instead?
   *`secrets.token_hex` or `secrets.token_urlsafe`.*
