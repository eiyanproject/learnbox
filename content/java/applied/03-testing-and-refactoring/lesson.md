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

## Test behaviour, not implementation

```java
// brittle: breaks when you switch List to Map, even though nothing broke
assertEquals(1, cart.getItemsList().size());

// durable: describes what the cart does
assertEquals(2, cart.itemCount());
```

The first asserts *how* the cart is built. Change the internals and the test
fails while the program is fine — so you stop trusting the suite, which is
worse than having none.

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

One behaviour per test, and a name that says what it is. A test called
`testCart1` tells you nothing when it fails at 3am; `discountAppliesToTheTotal`
tells you what stopped being true.

## Test the edges

The interesting cases are the boundaries: empty, one, the maximum, the invalid
input, the duplicate. Bugs congregate there, and the happy path is usually
covered by the program running at all.

## Then refactor

With behaviour pinned down, you can restructure freely — extract a method,
change a data structure, rename things — and the suite tells you within seconds
whether the behaviour survived. Without it, every change is a gamble and the
rational response is to stop changing anything, which is how code ossifies.

## Your turn

In `Cart.java`, a shopping cart:

- `addItem(String name, int quantity, double unitPrice)` — an existing name
  increases the quantity; a non-positive quantity is rejected
- `itemCount()` — total quantity across all lines
- `subtotal()` — before any discount
- `applyCoupon(String code)` — `SAVE10` is 10% off, `HALF` is 50% off,
  anything else throws
- `total()` — after the discount, rounded to 2 decimals
