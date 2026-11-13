---
title: "Round 2: Roman numerals"
summary: Numbers to Roman numerals and back, including the subtractive pairs that catch everyone.
order: 2
files: [Roman.java]
run: javac Roman.java && java Roman
challenge:
  minutes: 18
  xp: 200
  requires:
    xp: 700
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **Roman numeral** | a number written with the letters I, V, X, L, C, D, M |
| **symbol** | one of those letters, each with a value: I 1, V 5, X 10, L 50, C 100, D 500, M 1000 |
| **largest first** | numerals are written from the biggest symbol down and added up |
| **subtractive pair** | a smaller symbol before a larger one, meaning the difference: IV 4, IX 9, XL 40, XC 90, CD 400, CM 900 |
| **round trip** | converting there and back gives the original: `fromRoman(toRoman(n)) == n` |
| **range** | here 1 to 3999; anything else is rejected |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Roman.java && java Roman` | builds and runs this round's file |

### Java names

| Name | What it does |
|---|---|
| `static String toRoman(int n)` | number to numeral |
| `static int fromRoman(String s)` | numeral to number |
| `int[] values = {1000, 900, ...}`, `String[] symbols` | two arrays kept in step |
| `new StringBuilder()`, `sb.append(...)` | builds the numeral |
| `s.charAt(i)` | one symbol |
| `throw new IllegalArgumentException(...)` | rejects a number outside 1 to 3999 |

### Errors

| Error | Means |
|---|---|
| `IllegalArgumentException` | `toRoman` was given 0, a negative number, or more than 3999 |

---

The museum's new labels need their dates in Roman numerals, and the old
labels need reading back.

## The symbols

| Symbol | Value |
|---|---|
| `I` | 1 |
| `V` | 5 |
| `X` | 10 |
| `L` | 50 |
| `C` | 100 |
| `D` | 500 |
| `M` | 1000 |

A numeral is written largest first and added up: `VIII` is 8, `MDCLXVI` is
1666. Six **subtractive pairs** stand for what would otherwise take four of
the same symbol: `IV` is 4, `IX` is 9, `XL` is 40, `XC` is 90, `CD` is 400
and `CM` is 900. So 1994 is `MCMXCIV`: 1000, 900, 90, 4.

## The task

In `Roman.java`, write two static methods.

`String toRoman(int n)` converts 1 to 3999. Any other number throws
`IllegalArgumentException`.

```text
toRoman(4)     ->  "IV"
toRoman(49)    ->  "XLIX"
toRoman(2024)  ->  "MMXXIV"
```

`int fromRoman(String s)` converts back. You may assume `s` is a correctly
written upper-case numeral.

```text
fromRoman("XLIX")     ->  49
fromRoman("MCMXCIV")  ->  1994
```

For every `n` from 1 to 3999, `fromRoman(toRoman(n))` is `n`. And `toRoman`
never writes the same symbol four times in a row: 4 is `IV`, never `IIII`,
and 40 is `XL`, never `XXXX`. A test checks every number for that.
