---
title: "Round 3: Fractions"
summary: A value type with operators. Keep it in lowest terms and it compares, prints and adds correctly for free.
order: 3
files: [fraction.cpp, fraction.h]
run: g++ -std=c++20 -Wall -c fraction.cpp
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 420
---

The recipe scaler keeps printing `0.33333334 cups`. It needs exact
fractions.

## The task

`fraction.h` declares the class `Fraction`. Define its members and the free
operators in `fraction.cpp`. Do not change the header.

A `Fraction` is always stored **normalised**:

- in lowest terms: `Fraction(2, 4)` holds 1 and 2
- with the sign on the numerator: `Fraction(1, -2)` holds -1 and 2
- zero is always `0/1`

Because of that, two equal fractions always hold the same two numbers.

- `Fraction(long long numerator, long long denominator = 1)` throws
  `std::invalid_argument` when the denominator is `0`.
- `numerator()` and `denominator()` return the stored values.
- `+`, `-`, `*` and `/` return a new normalised `Fraction`. Dividing by a
  fraction that is zero throws `std::invalid_argument`.
- `==` compares values. `<` compares values too: 1/3 is less than 1/2.
- `to_string()` is `"3/4"`, or just `"5"` when the denominator is 1, with a
  leading `-` for negatives: `"-1/2"`.

```cpp
Fraction a(1, 2), b(1, 3);
(a + b).to_string();          // "5/6"
(a * b).to_string();          // "1/6"
(a / b).to_string();          // "3/2"
Fraction(6, -8).to_string();  // "-3/4"
Fraction(4, 2).to_string();   // "2"
```

`std::gcd` in `<numeric>` does the reducing.
