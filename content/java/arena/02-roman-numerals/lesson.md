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

For every `n` from 1 to 3999, `fromRoman(toRoman(n))` is `n`.
