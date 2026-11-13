---
title: How passwords are stored and attacked
summary: Why a fast hash is the problem, what entropy really measures, the slow KDF that fixes storage, and comparing secrets without leaking their length.
order: 3
files: [passwords.py]
run: python passwords.py
hints:
  - "`estimate_bits`: find which character classes appear (lower 26, upper 26, digits 10, other 33), add up the pool size, and return `len(password) * log2(pool)`. Empty password is 0 bits."
  - "`slow_hash`: `hashlib.pbkdf2_hmac('sha256', password, salt, iterations)` then `.hex()`. The iteration count is what makes it slow on purpose."
  - "`constant_time_equal`: if the lengths differ return False, then OR together `x ^ y` for every pair and return whether the total is 0 - no early exit on the first difference."
  - "`is_strong`: at least 60 estimated bits AND the lowercased password is not one of the common ones."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **fast hash** | a hash built for speed, like SHA-256: good for checking files, bad for passwords |
| **GPU** | a graphics card; it computes billions of simple hashes a second, which is why attackers use them |
| **guess** | one attempt at a password: hash it, compare it with the stolen digest |
| **key derivation function** (KDF) | a hash made slow on purpose, for storing passwords: PBKDF2, scrypt, bcrypt, Argon2 |
| **PBKDF2** | a KDF that repeats HMAC thousands of times; built into Python |
| **Argon2id, scrypt, bcrypt** | stronger KDFs that also need a lot of memory, which GPUs are short of; Argon2id is the first choice today |
| **iterations** (work factor) | how many times the KDF repeats; more is slower for the attacker and for you |
| **derived key** | what a KDF outputs; it is what gets stored instead of the password |
| **asymmetry** | the user pays the slow cost once per login; the attacker pays it once per guess |
| **entropy** | how unpredictable a password is, in **bits**: each extra bit doubles the number of guesses needed |
| **bits of entropy** | the base-2 logarithm of how many passwords an attacker would have to try |
| **character pool** | how many different characters a password could use: 26 lowercase, 26 uppercase, 10 digits, 33 symbols |
| **character class** | one of those four groups |
| **ceiling** | the highest the real value could be; the entropy estimate is one, because people do not choose randomly |
| **breach corpus** | lists of real passwords leaked from hacked websites; attackers try these first |
| **blocklist** | a list of values to refuse, such as the most common passwords |
| **side channel** | information that leaks from how a program behaves (time, power, errors) rather than from what it outputs |
| **timing side channel** | a leak through how long an operation takes |
| **early exit** | a loop that stops as soon as it knows the answer; in a comparison, this is the leak |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python passwords.py` | runs your program, printing three passwords with their estimated bits and whether they are strong |

### Python names

| Name | What it does |
|---|---|
| `from math import log2` | loads the base-2 logarithm: `log2(8)` is `3.0` |
| `round(x, 1)` | `x` rounded to one decimal place |
| `len(password)` | the number of characters |
| `c.islower()`, `c.isupper()`, `c.isdigit()` | `True` when the character is a lowercase letter, an uppercase letter, a digit |
| `c.isalnum()` | `True` for a letter or a digit, so `not c.isalnum()` means "a symbol" |
| `any(... for c in password)` | `True` when the test is true for at least one character |
| `hashlib.pbkdf2_hmac("sha256", password, salt, iterations)` | the PBKDF2 derived key, as bytes |
| `.hex()` | bytes as a string of hex digits |
| `200_000` | the number 200000; the underscore only makes it easier to read |
| `zip(a, b)` | pairs up the items of `a` and `b`: first with first, second with second |
| `x ^ y` | XOR of two numbers: 0 when they are equal, something else when they differ |
| `result \|= value` | sets `result` to `result \| value` (bitwise OR), so any 1 bit ever seen stays set |
| `password.lower()` | the password in lowercase, so `Password` matches `password` |
| `in COMMON` | `True` when the value is in the set `COMMON` |
| `f"{pw:30}"`, `f"{bits:6.1f}"` | pads text to 30 characters; prints a number 6 wide with 1 decimal |

---

The last lesson ended with a problem: a salt is needed, but it is not
enough. The other half of storing passwords safely is **speed**, and the
answer is surprising: a **slower** hash is a **safer** one.

## Why a fast hash loses

SHA-256 is designed to be fast. One graphics card (**GPU**) computes billions
of SHA-256 digests a second. That is what you want when checking a
download, and exactly what you do **not** want for passwords: an attacker
who has stolen your database runs those same billions of **guesses** a
second against it.

A salt stops one precomputed table from cracking every account at once
(previous lesson). It does nothing to slow down the guesses against one
account. A weak password with a salt still falls in seconds.

## The fix: a slow hash on purpose

A **key derivation function** (KDF) is a hash built to be slow. **PBKDF2**,
which Python has built in, repeats an HMAC many thousands of times; the
number of repeats is the **iteration count**:

```python
hashlib.pbkdf2_hmac("sha256", password, salt, 200_000)
```

Now each guess costs the attacker 200,000 hashes instead of one.

- An honest user logs in once. They wait a fraction of a second and never
  notice.
- An attacker trying a billion guesses pays the cost a billion times, and
  what took a minute now takes months.

That **asymmetry** is the whole design. The current advice (OWASP's Password
Storage Cheat Sheet) is to use **Argon2id** where you can: it is slow and
also needs a lot of memory, which graphics cards are short of. **scrypt** and
**bcrypt** are older but fine. If PBKDF2 has to be used, OWASP recommends
600,000 iterations of HMAC-SHA256. On this machine that takes about 0.2
seconds, once per login.

```pycon
>>> from passwords import slow_hash
>>> slow_hash(b"pw", b"salt", 1000)
'0a38253555ce37f5c72a6b703f996814ebf241f203af146e93dcdeb031c5567e'
```

The stored value is this **derived key**, together with the salt and the
iteration count, so the server can repeat the same calculation at the next
login and compare.

## Entropy: how hard is a password to guess?

Password strength is measured in **bits of entropy**. If an attacker would
need to try 2 to the power of *n* passwords to be sure of finding yours, the
password has *n* bits. Each extra bit doubles the work.

A rough estimate:

1. Work out the **character pool**, the number of characters the password
   could have used. Add 26 if it has any lowercase letter, 26 more for any
   uppercase letter, 10 for any digit, and 33 for any other character (the
   symbols on a keyboard, roughly).
2. Multiply the length by `log2(pool)`, the bits each character adds.

```pycon
>>> from math import log2
>>> round(6 * log2(26 + 26 + 10 + 33), 1)    # P@ss1!: 6 characters, every class
39.4
>>> round(20 * log2(26), 1)                   # 20 random lowercase letters
94.0
```

Twenty random lowercase letters beat six characters of every kind by a huge
margin. **Length matters far more than "complexity"**, because each extra
character multiplies the work, while an extra character class only adds a
few bits.

### What the estimate does not know

The estimate assumes every character was picked at **random**, and real
passwords are not. So the number is a **ceiling**: the best case. The real
strength can only be lower, sometimes much lower.

- `correcthorsebatterystaple` scores about 117.5 bits by this sum. But it is
  four ordinary words, and attackers guess **words**, not letters. Four words
  picked at random from a 2,048-word list are about **44 bits**: still
  reasonable, and less if a person chose the words rather than a dice roll.
- `password1234567890` also scores high, and is worthless: a dictionary word
  with a predictable ending, which every cracking tool tries in seconds.

That is why real systems use the estimate only as a first check, and also
refuse any password found in a **breach corpus**, the lists of real passwords
leaked from hacked websites. The tiny **blocklist** in this lesson,
`COMMON`, stands in for one. Never treat the number as a guarantee.

## Comparing without leaking

Checking an API token, a session ID or an HMAC tag means comparing a stored
secret with a value the attacker sends. A plain `==` stops at the first byte
that differs (an **early exit**). So the time it takes shows how many leading
bytes were right: a **timing side channel**, which lets an attacker find the
secret one byte at a time.

A constant-time comparison looks at every byte every time. The trick:

1. If the lengths differ, return `False`.
2. Go through the bytes in pairs. `x ^ y` (XOR) is `0` when two bytes are
   equal and something else when they differ.
3. OR every result into one total with `|=`. Once any bit is 1, it stays 1.
4. At the end, the strings were equal only if the total is still `0`.

The loop always runs to the end, so the time does not depend on where the
first difference was. Real code uses `hmac.compare_digest`, which does the
same thing in C.

(For a stored password, the attacker compares against a **hash**, whose
bytes they cannot steer, so the leak helps them much less. Still compare in
constant time: it costs nothing, and it saves deciding which comparisons are
safe to get wrong.)

## Your turn

In `passwords.py`:

- `estimate_bits(password)`: the estimated entropy in bits,
  `length * log2(pool)` as above, and `0.0` for an empty password.
- `slow_hash(password, salt, iterations)`: the PBKDF2-HMAC-SHA256 derived
  key as a hex string (`password` and `salt` are bytes).
- `constant_time_equal(a, b)`: compare two byte strings with no early exit.
- `is_strong(password)`: at least 60 estimated bits, **and** its lowercase
  form is not in `COMMON`.

Run it:

```text
P@ss1!                           39.4 bits  strong=False
qvhtzmkwbrpxlnjdafcs             94.0 bits  strong=True
password                         37.6 bits  strong=False
```

## Check yourself

1. Why is SHA-256 a bad choice for storing passwords, even with a salt?
   *It is fast, so an attacker can try billions of guesses a second.*
2. What does raising the iteration count do to the user, and to the
   attacker?
   *The user waits a little longer once; every one of the attacker's guesses
   costs that much more.*
3. Which is stronger: 8 characters of every class, or 16 random lowercase
   letters?
   *16 lowercase letters: about 75 bits against about 53.*
4. Why is the entropy estimate only a ceiling?
   *It assumes random characters; real passwords use words and patterns.*
5. How does the constant-time comparison avoid an early exit?
   *It ORs together the XOR of every pair of bytes and checks the total only
   at the end.*
