---
title: Loops
summary: Repeat work with for and while, count with range, and steer with break and continue.
order: 6
files: [loops.py]
run: python -i loops.py
hints:
  - "`sum_to(n)`: start `total = 0`, loop `for i in range(1, n + 1)`, add each `i`."
  - "`fizzbuzz(n)` builds a list: `result = []`, then `result.append(...)` inside the loop. Check divisible-by-15 first."
  - "`collatz_steps(n)`: `while n != 1:` apply the rule and count how many times the loop runs."
  - "`first_repeated(words)`: keep a `seen` list or set; for each word, if it is already in `seen`, return it straight away."
---

## for

`for` runs a block once for every item in a sequence:

```python
for fruit in ["apple", "mango", "durian"]:
    print(fruit)

for ch in "abc":
    print(ch)
```

## range

`range` produces numbers to loop over. Like slicing, the stop value is not
included:

```python
range(5)          # 0, 1, 2, 3, 4
range(1, 6)       # 1, 2, 3, 4, 5
range(0, 10, 2)   # 0, 2, 4, 6, 8
range(5, 0, -1)   # 5, 4, 3, 2, 1
```

Adding things up is a pattern you will write constantly:

```python
total = 0
for n in range(1, 11):
    total += n
print(total)   # 55
```

## Building a list

Start empty and `append` as you go:

```python
squares = []
for n in range(5):
    squares.append(n * n)
# [0, 1, 4, 9, 16]
```

## enumerate

When you need the position as well as the item:

```python
for i, name in enumerate(["Ana", "Budi"], start=1):
    print(i, name)     # 1 Ana, then 2 Budi
```

## while

`while` repeats as long as its condition stays true. Use it when you do not
know in advance how many times to go round:

```python
n = 1
while n < 1000:
    n *= 2
print(n)   # 1024
```

If the condition never becomes false, the loop never ends. In the terminal,
Ctrl+C stops a runaway program; a **Check** that loops forever is stopped by
a time limit.

## break and continue

```python
for n in range(2, 100):
    if n % 7 == 0:
        print("first multiple of 7:", n)
        break          # leave the loop entirely

for n in range(10):
    if n % 2 == 0:
        continue       # skip to the next item
    print(n)           # prints only odd numbers
```

Inside a function, `return` also ends the loop, because it ends the whole
function.

## Your turn

In `loops.py`, write:

- `sum_to(n)`: the sum 1 + 2 + ... + n (`sum_to(0)` is 0). Use a loop, even
  though `sum(range(...))` exists.
- `fizzbuzz(n)`: a list of strings for 1 to n. Multiples of 3 become `"Fizz"`,
  of 5 `"Buzz"`, of both `"FizzBuzz"`, and anything else its number as text:
  `fizzbuzz(5)` is `["1", "2", "Fizz", "4", "Buzz"]`
- `collatz_steps(n)`: how many steps it takes to reach 1 if you repeatedly
  halve even numbers and turn odd numbers into `3 * n + 1`. `collatz_steps(1)`
  is 0, `collatz_steps(6)` is 8.
- `first_repeated(words)`: the first word that appears for a second time,
  or `None` if no word repeats
