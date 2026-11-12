---
title: Tests that let you change things
summary: Testing behaviour rather than implementation, the arrange-act-assert shape, and refactoring under a green suite.
order: 3
files: [Cart.java]
run: javac Cart.java && java Cart
hints:
  - "`total()` applies the discount AFTER summing, and rounds to 2 decimals: `Math.round(value * 100) / 100.0`."
  - "`addItem` with an existing name should increase the quantity rather than adding a second line - that is the behaviour the test checks, not how you store it."
  - "`applyCoupon` rejects an unknown code with IllegalArgumentException and accepts SAVE10 (10%) and HALF (50%)."
  - "`itemCount` is the total quantity, not the number of distinct lines - two apples and one pear is 3."
---

A test suite is not there to prove code works. It is there so you can **change**
code and find out immediately whether you broke something. That difference
decides how you write them.

The tests in this course are **JUnit** tests: classes with methods marked
`@Test`, which the JUnit runner finds and calls one by one. Inside, an
**assertion** checks one fact and fails the test, with both values in the
message, if it is false:

- `assertEquals(expected, actual)` — the two must be equal. For `double`s, a
  third argument gives the tolerance, because floating-point sums are rarely
  exact: `assertEquals(2.70, total, 0.001)` passes for anything within 0.001
  of 2.70.
- `assertTrue(condition)` and `assertFalse(condition)`.
- `assertThrows(SomeException.class, () -> ...)` — passes only if the lambda
  throws that exception.

In this lesson the tests already exist and you write the code. Read them, in
`tests/`, as examples of the style described here.

## Test behaviour, not implementation

```java
// brittle: breaks when you switch List to Map, even though nothing broke
assertEquals(1, cart.getItemsList().size());

// durable: describes what the cart does
assertEquals(2, cart.itemCount());
```

(Two alternative assertions.) The first asserts *how* the cart is built: it
reaches into the cart for its internal list. Change the internals and the test
fails while the program is fine — so you stop trusting the suite, which is
worse than having none. A test that fails when nothing is broken trains
everyone to ignore failures, including the real ones. Tests tied to internals
like this are called **brittle**.

Ask of each assertion: *if I rewrote the internals completely but kept the
behaviour, would this still pass?* If not, it is testing the wrong thing.

## Arrange, act, assert

```java
@Test
void discountAppliesToTheTotal() {
    Cart cart = new Cart();                 // arrange
    cart.addItem("apple", 2, 1.50);

    cart.applyCoupon("SAVE10");             // act

    assertEquals(2.70, cart.total(), 0.001); // assert
}
```

Every test has the same three parts. **Arrange** sets up the situation: a
cart with two apples at 1.50. **Act** does the one thing being tested: apply
the coupon. **Assert** checks the outcome: 3.00 less 10% is 2.70. A blank
line between the parts makes every test read the same way.

One behaviour per test, and a name that says what it is. A test called
`testCart1` tells you nothing when it fails at 3am; `discountAppliesToTheTotal`
tells you what stopped being true. A test that checks several behaviours stops
at its first failure, and hides whether the rest still work.

## Test the edges

The interesting cases are the boundaries: empty, one, the maximum, the invalid
input, the duplicate. Bugs congregate there, and the happy path is usually
covered by the program running at all. For a cart that means: an empty cart,
adding the same item twice, a quantity of zero or less, an unknown coupon, a
coupon applied before any items are added, and a total that needs rounding.
This lesson's tests check every one of those.

## Test first

Writing the test before the code is called **test-driven development**
(TDD). The cycle, repeated for each small piece of behaviour:

1. **Write one test** for a behaviour that does not exist yet.
2. **Run it, and watch it fail.** A new test that passes straight away is
   testing nothing new, or is wrong.
3. **Write just enough code** to make it pass, and no more.
4. **Run all the tests.** If any fail, fix the code (or, if the code is
   right, the newest test).
5. **Tidy up** the code (next section), running the tests after each change.

Working in small steps like this means you always know which change broke
something: the last one.

## When a test fails

A checklist for when you do not know where the problem is:

1. **Read the failure message.** JUnit shows the expected and actual values;
   the difference often names the bug (`expected 2.70 but was 3.0` says the
   discount was never applied).
2. **Read the stack trace** if an exception was thrown, and find the first
   line in your own file (Environment lesson 1).
3. **Run that one test alone**, and try the same input yourself in `main` or
   `jshell`.
4. **Print the values** of the variables involved at each step, and compare
   with what you expected.
5. **Check the edge**: is it the empty case, the duplicate, the zero?

## Then refactor

**Refactoring** means changing the structure of code without changing what
it does: extracting a method, choosing a different data structure, renaming
things. With behaviour pinned down by tests, you can restructure freely, and
the suite tells you within seconds whether the behaviour survived. Without it,
every change is a gamble and the rational response is to stop changing
anything, which is how code ossifies.

The cart is a good example. You might first store the lines in a `List`, then
realise a `Map` from name to quantity makes "add the same item again" simpler.
The tests here only call `addItem`, `itemCount`, `subtotal`, `applyCoupon` and
`total`, so you can make that switch and they keep passing: they test the
behaviour, not the list.

## Your turn

In `Cart.java`, a shopping cart:

- `addItem(String name, int quantity, double unitPrice)` — adding a name that
  is already in the cart increases its quantity instead of adding a second
  line; a quantity of zero or less is rejected with
  `IllegalArgumentException`
- `itemCount()` — the total quantity across all lines (two apples and one
  pear is 3); `0` for an empty cart
- `subtotal()` — the sum of quantity times unit price, before any discount
- `applyCoupon(String code)` — `SAVE10` is 10% off, `HALF` is 50% off,
  anything else throws `IllegalArgumentException`. The coupon applies to the
  whole cart, including items added after it.
- `total()` — the subtotal after the discount, rounded to 2 decimals
  (`Math.round(value * 100) / 100.0`). Three items at 0.335 come to 1.005,
  which rounds to `1.01`. An empty cart's total is `0.0`.
