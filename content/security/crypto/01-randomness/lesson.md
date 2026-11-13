---
title: Randomness that can be trusted
summary: The difference between random and secrets, why a predictable generator undoes a whole system, and reproducing a weak token to prove it.
order: 1
files: [rng.py]
run: python rng.py
hints:
  - "`secure_token`: `import secrets`, then `secrets.token_hex(n_bytes)` - a string twice as long as the byte count."
  - "`weak_token`: `random.Random(seed).getrandbits(32)`. The same seed always gives the same number, which is exactly the flaw."
  - "`predict`: make one `random.Random(seed)`, pull `n` values from it in a row, and return the last. A server reusing a guessable seed hands you its whole sequence."
  - "`enough_entropy`: 16 bytes is 128 bits, the usual floor for a token."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **random** | impossible to predict, even for someone who has seen every earlier value |
| **token** | a random string that proves something: a logged-in session, a password-reset link, an API key |
| **session token** | the value a website stores in your browser after you log in; whoever has it is you |
| **nonce** | a "number used once", which some encryption needs fresh every time |
| **true random number generator** | one that measures a physical process, such as electrical noise |
| **pseudo-random number generator** (PRNG) | a calculation that produces numbers which look random but follow from a starting value |
| **seed** | the starting value of a PRNG; the same seed always gives the same sequence |
| **reproducible** | gives the same results every time from the same start; good for tests and games |
| **predictable** | an outsider can work out the next value |
| **CSPRNG** (cryptographically secure PRNG) | a generator whose output cannot be predicted from earlier output |
| **operating system's random source** | the kernel's CSPRNG (`/dev/urandom`, `getrandom`), fed by hardware events |
| **Mersenne Twister** | the PRNG behind Python's `random`; after 624 of its outputs, all later ones can be calculated |
| **entropy** | how many bits of unpredictability a value really has |
| **128 bits** | the usual minimum for a token: 2 to the power 128 guesses is far beyond any computer |
| **brute force** | trying every possible value |
| **URL-safe** | uses only characters that can go in a web address without escaping |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python rng.py` | runs your program: one secure token, one weak one, and a predicted one |
| `head -c 16 /dev/urandom \| xxd -p` | 16 random bytes straight from the kernel, as hex |

### Python names

| Name | What it does |
|---|---|
| `import secrets` | loads the module for unguessable values |
| `secrets.token_hex(16)` | 16 random bytes, as 32 hex characters |
| `secrets.token_urlsafe(16)` | 16 random bytes, as about 22 URL-safe characters |
| `secrets.choice(items)` | one item, picked securely |
| `import random` | loads the module for simulations and games: **not** for secrets |
| `random.Random(seed)` | a PRNG of its own, started from `seed` |
| `.getrandbits(32)` | the next 32-bit number from that generator (0 to 4,294,967,295) |
| `for _ in range(n):` | repeat `n` times; `_` means "the counter is not used" |
| `value = None` | a starting value that means "nothing yet" |
| `n_bytes * 8` | the bits in that many bytes |

---

Almost every security mechanism depends on an attacker being unable to
**guess** a value: a **session token** (whoever has it is logged in as you),
a password-reset link, a key, a **nonce**. All of that protection comes from
one thing, the quality of the random numbers. And it is easy to pick the
wrong tool without noticing.

## Two kinds of random

Computers are built to be predictable, so producing randomness takes work.
There are two approaches:

- A **pseudo-random number generator** (PRNG) is a calculation. You give it
  a starting value, the **seed**, and it produces a long sequence of numbers
  that look random. But the whole sequence follows from the seed: the same
  seed always gives the same sequence. That is useful for a game or a
  simulation that you want to repeat exactly.
- A **cryptographically secure** generator (CSPRNG) is built so that nobody
  can predict its next output, even after seeing everything it produced
  before. The operating system runs one, fed by unpredictable hardware events
  (timings of disks, network packets, keyboard presses).

Python has one module for each, and they look alike:

| Module | Kind | Use it for |
|---|---|---|
| `random` | PRNG (the Mersenne Twister) | games, simulations, shuffling test data |
| `secrets` | the operating system's CSPRNG | **anything an attacker must not guess** |

```pycon
>>> import secrets
>>> len(secrets.token_hex(16))     # 16 random bytes, as 32 hex characters
32
>>> secrets.token_urlsafe(16)      # safe inside a URL; different every time
'...'
>>> secrets.choice(["red", "green", "blue"])   # a secure pick
'...'
```

(`'...'` stands for "some string": the real output is different on every
run.)

## Why a predictable generator is fatal

Seed `random` with the same value and it replays exactly the same numbers:

```pycon
>>> import random
>>> random.Random(42).getrandbits(32)
2746317213
>>> random.Random(42).getrandbits(32)     # same seed, same "random" number
2746317213
```

For a token, that is a disaster. Suppose a server seeds its generator with
the current time when it starts, a classic mistake, and then hands out
tokens from it. An attacker who can guess roughly when the server started
can try each possible second as the seed, run the same generator, and
produce every token the server will ever issue. No code is broken and no
mathematics is needed: they just run the same calculation.

Even without knowing the seed, the Mersenne Twister is not safe: after
seeing 624 of its 32-bit outputs, anyone can calculate all later ones.

You will write the first attack: given the seed, replay the sequence and
predict the *n*-th value.

```pycon
>>> from rng import predict
>>> predict(42, 1)                         # the first token: the same number as above
2746317213
>>> predict(42, 3)                         # the third token the server will issue
107420369
```

## The defence

1. Use `secrets` (or `os.urandom`) for every token, key, reset link and
   nonce. Never `random`.
2. Make the token long enough. **16 bytes, 128 bits**, is the usual minimum:
   2 to the power 128 guesses is far more than all the computers in the world
   could try, even against a perfect generator.

## Your turn

In `rng.py`:

- `secure_token(n_bytes=16)`: an unguessable hex token of `n_bytes` random
  bytes from `secrets` (so `2 * n_bytes` hex characters).
- `weak_token(seed)`: `random.Random(seed).getrandbits(32)`, a 32-bit number
  from a generator seeded with `seed`. The same seed always returns the same
  number, and that is the point.
- `predict(seed, n)`: the `n`-th token (counting from 1) that a server would
  issue if it seeded `random` with `seed` and handed out `getrandbits(32)`
  values in order.
- `enough_entropy(n_bytes)`: `True` when a token of that many random bytes
  carries at least 128 bits (each byte is 8 bits).

## Check yourself

1. What is a seed?
   *The starting value of a pseudo-random generator; the same seed gives the
   same sequence.*
2. Why is `random` wrong for a password-reset token?
   *Its output is predictable from its seed, or from earlier outputs.*
3. A server seeds `random` with the time it started. How does an attacker
   predict its tokens?
   *Try each likely start time as the seed and run the same generator.*
4. How many random bytes make a 128-bit token?
   *16.*
5. Which Python module should make session tokens?
   *`secrets`.*
