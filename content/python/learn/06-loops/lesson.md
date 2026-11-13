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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **loop** | code that runs the same block several times |
| **collection** | a value holding several items, such as a list or a string |
| **loop variable** | the name after `for`, set to the next item each time round |
| **iteration** | one run of the loop's body; **iterating** is going through a collection item by item |
| **range** | a run of whole numbers handed out one at a time; the stop value is not included |
| **accumulator** | a variable that collects a running result, such as a total starting at `0` |
| **empty list** (`[]`) | a list with no items, the usual start when building a list |
| **pair** | two values handed over together, unpacked into two names |
| **infinite loop** | a loop whose condition never becomes false, so it never ends |
| **divisible** / **multiple** | divides with no remainder: `n % 3 == 0` |
| **Collatz rule** | halve an even number, replace an odd one with `3 * n + 1` |

### Python keywords and functions

| Name | What it does |
|---|---|
| `for item in collection:` | runs the body once per item |
| `range(stop)`, `range(start, stop)`, `range(start, stop, step)` | whole numbers from `start` (0 if left out) up to, not including, `stop` |
| `list(x)` | collects all the items into a list, for example to see a range |
| `+=`, `*=` | add to a variable; multiply it |
| `items.append(x)` | adds `x` to the end of a list |
| `enumerate(seq, start=1)` | gives position-and-item pairs: `for i, name in enumerate(...)` |
| `while condition:` | repeats while the condition is true, checked before each round |
| `break` | leaves the loop at once |
| `continue` | skips the rest of the body for this item, on to the next |
| `return` | ends the whole function, and so the loop too |
| `None` | "nothing here": the usual answer for "not found" |
| `sum(numbers)` | adds up the numbers |
| `in` | checks whether a value is in a collection: `word in seen` |
| `//` | floor division, keeps a number an `int` |

### Keys

| Key | What it does |
|---|---|
| Ctrl+C | stops a running program, such as an infinite loop |

---

A **loop** runs the same block of code several times. Python has two kinds:
`for`, which goes through a collection of items one by one, and `while`,
which keeps going as long as a condition stays true. Between them they cover
almost every kind of repetition you will need.

## for

`for` runs a block once for every item in a sequence, such as a list or a
string:

```python
for fruit in ["apple", "mango", "durian"]:
    print(fruit)

for ch in "abc":
    print(ch)
```

```output
apple
mango
durian
a
b
c
```

Read `for fruit in [...]:` as "for each fruit in this list, do the
following". The name after `for`, here `fruit`, is the **loop variable**.
Each time round, Python sets it to the next item and runs the indented body.
When the items run out, the loop ends and the program carries on with the
first line after the body. You choose the loop variable's name; pick one that
says what a single item is.

Each run of the body is called an **iteration**, and going through a
collection item by item is called **iterating** over it.

## range

`range` produces a run of whole numbers to loop over, which is how you
repeat something a set number of times. It takes up to three numbers, the
same start, stop and step as a slice, and like slicing, the stop value is not
included:

```pycon
>>> list(range(5))          # list() shows all the numbers at once
[0, 1, 2, 3, 4]
>>> list(range(1, 6))
[1, 2, 3, 4, 5]
>>> list(range(0, 10, 2))   # a step of 2
[0, 2, 4, 6, 8]
>>> list(range(5, 0, -1))   # counting down
[5, 4, 3, 2, 1]
```

`range(5)` gives five numbers, 0 to 4, so `for i in range(5):` runs its body
exactly five times. To count from 1 to n inclusive, write `range(1, n + 1)`.

A range does not store its numbers; it hands them out one at a time as the
loop asks for them, which is why `range(1_000_000)` costs no memory. If you
type `range(5)` at the prompt, Python only shows `range(0, 5)`. Wrapping it in
`list()` collects the numbers into a list so you can see them all at once.

Adding things up is a pattern you will write constantly: start a total at
zero, then add to it once per item:

```python
total = 0
for n in range(1, 11):
    total += n
print(total)
```

```output
55
```

Going round by round: `total` starts at 0. The first time, `n` is 1, so
`total` becomes 1. Then `n` is 2 and `total` becomes 3, then 6, 10, 15, and so
on up to 55 after `n` is 10. A variable used like this is called an
**accumulator**: it collects a running result as the loop goes.

Two details matter. `total = 0` is *before* the loop, so it happens once; put
it inside and it would be reset every time round. And `print(total)` is *not*
indented, so it runs once, after the loop has finished; indent it and you
would see every intermediate total instead.

## Building a list

The same pattern builds a list: start with an empty list, `[]`, and `append`
an item each time round. `append` adds one item to the end of a list:

```python
squares = []
for n in range(5):
    squares.append(n * n)
print(squares)
```

```output
[0, 1, 4, 9, 16]
```

## enumerate

A `for` loop gives you each item but not its position. When you need both,
wrap the sequence in `enumerate()`. Each time round it hands you a pair, the
position and the item, and writing two names after `for` unpacks the pair,
the same way `low, high = ...` unpacked a returned pair. Positions count from
0 unless you pass `start=` to choose where to begin:

```python
for i, name in enumerate(["Ana", "Budi"], start=1):
    print(i, name)
```

```output
1 Ana
2 Budi
```

## while

`while` repeats as long as its condition stays true. Use it when you do not
know in advance how many times to go round, only when to stop. "Keep doubling
until the number reaches 1000" is a `while` loop; "do this for each item" is a
`for` loop.

```python
n = 1
while n < 1000:
    n *= 2
print(n)
```

```output
1024
```

The condition is checked *before* each round, including the first. `n` goes
1, 2, 4, 8 and so on. When `n` is 512 the condition is still true, so the
body runs once more and `n` becomes 1024. The next check, `1024 < 1000`, is
false, so the loop stops and the line after it prints 1024. If the condition
is false from the start, the body never runs at all.

Something in the body must eventually make the condition false. If nothing
does, the loop never ends: an **infinite loop**. Forgetting the line that
changes the variable (`n *= 2` here) is the usual cause. In the terminal,
Ctrl+C stops a runaway program; a **Check** that loops forever is stopped by
a time limit.

## break and continue

Two statements change what a loop does partway through. `break` leaves the
loop at once, skipping any items that are left; it is how you stop early once
you have found what you were looking for. `continue` skips the rest of the
body for the current item only, and moves straight on to the next one.

```python
for n in range(2, 100):
    if n % 7 == 0:
        print("first multiple of 7:", n)
        break          # leave the loop entirely

for n in range(10):
    if n % 2 == 0:
        continue       # skip to the next item
    print(n)           # so only odd numbers get here
```

```output
first multiple of 7: 7
1
3
5
7
9
```

In the first loop, `range(2, 100)` would go all the way to 99, but `break`
stops it at 7, the first number that divides by 7. In the second, the even
numbers hit `continue`, so the `print` below it is skipped for them.

Inside a function, `return` also ends the loop, because it ends the whole
function. That is often the neatest way to stop early: return the answer the
moment you find it, and put the "not found" result after the loop, where it
is only reached if the loop ran to the end without returning.

## Your turn

In `loops.py`, write:

- `sum_to(n)`: the sum 1 + 2 + ... + n, so `sum_to(4)` is 10 and `sum_to(0)`
  is 0. Use a loop, even though `sum(range(...))` exists.
- `fizzbuzz(n)`: a list of strings, one for each number from 1 to n.
  Multiples of 3 become `"Fizz"`, multiples of 5 become `"Buzz"`, multiples
  of both (that is, of 15) become `"FizzBuzz"`, and every other number
  becomes its number as text, such as `"4"`:
  `fizzbuzz(5)` is `["1", "2", "Fizz", "4", "Buzz"]`. Check for 15 first:
  15 is also a multiple of 3, so a "multiple of 3" check placed earlier would
  catch it and give `"Fizz"`.
- `collatz_steps(n)`: start from `n` and apply one rule over and over until
  you reach 1. If the number is even, halve it; if it is odd, replace it with
  `3 * n + 1`. Return how many times you applied the rule. From 6 the numbers
  go 3, 10, 5, 16, 8, 4, 2, 1, which is eight steps, so `collatz_steps(6)` is
  8. `collatz_steps(1)` is 0: it is already there. You do not know in advance
  how many steps it will take, which makes this a job for `while`. Use `//`
  to halve, so the number stays an `int`.
- `first_repeated(words)`: go through the list in order and return the first
  word you have already seen, or `None` if no word repeats. Keep a record of
  the words you have passed so far, and check each new word against it before
  adding it.
  `first_repeated(["a", "b", "c", "b", "a"])` is `"b"`: `b` is the first to
  turn up a second time, even though `a` appeared earlier.
