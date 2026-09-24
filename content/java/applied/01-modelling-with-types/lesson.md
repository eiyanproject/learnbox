---
title: Modelling a domain with types
summary: Making illegal states unrepresentable - records for data, enums for closed sets, and validation in the constructor rather than everywhere else.
order: 1
files: [Booking.java]
run: javac Booking.java && java Booking
hints:
  - "`Status` is an enum with PENDING, CONFIRMED and CANCELLED. An enum can hold fields and methods - give it `boolean isFinal()` returning true for CANCELLED."
  - "`Booking` is a record with a compact constructor that validates: `Booking { if (guests < 1) throw ... }` - no parameter list, no assignments."
  - "`confirm()` returns a NEW Booking with the status changed, because a record is immutable. `new Booking(reference, guests, Status.CONFIRMED)`."
  - "Reject a null or blank reference too - `reference == null || reference.isBlank()`."
---

The certification tracks teach the language. This one is about using it: the
first job in any real program is deciding what the types are.

The goal is a design where **wrong states cannot be built**. Every check you
put in the constructor is a check the rest of the program never has to repeat.

## Enums for closed sets

A booking is pending, confirmed or cancelled. Three states, known in advance:

```java
enum Status { PENDING, CONFIRMED, CANCELLED }
```

Not a `String`, which admits `"confrimed"`. Not an `int`, which admits 47. The
compiler now checks every use, `switch` can be exhaustive without a `default`,
and the set of possibilities is written down in one place.

Enums are full classes: they can hold fields, constructors and methods, which
is how behaviour that varies by case lives with the case rather than in a
`switch` somewhere else.

## Records for data

```java
record Booking(String reference, int guests, Status status) {}
```

Immutable, with `equals`, `hashCode`, `toString` and accessors generated. The
compact constructor is where validation goes:

```java
record Booking(String reference, int guests, Status status) {
    Booking {
        if (guests < 1) throw new IllegalArgumentException("at least one guest");
    }
}
```

No parameter list, no assignments — the compiler adds those after your code
runs. From that moment, a `Booking` in hand is a valid one, everywhere, with no
further checking.

## Changing immutable data

You do not. You derive a new value:

```java
Booking confirm() { return new Booking(reference, guests, Status.CONFIRMED); }
```

That looks wasteful and almost never is. What it buys is that no other part of
the program can change a booking behind your back — the single largest source
of "how did it get into that state" bugs.

## Fail fast

Validate at the boundary, throw immediately, and name what was wrong. A
constructor that accepts nonsense pushes the failure somewhere far away, where
the stack trace no longer points at the cause.

## Your turn

In `Booking.java`:

- `enum Status { PENDING, CONFIRMED, CANCELLED }` with
  `public boolean isFinal()` — true only for `CANCELLED`
- `record Booking(String reference, int guests, Status status)` validating that
  the reference is not null or blank and that guests is at least 1
- `Booking confirm()` and `Booking cancel()` returning new bookings
- `static Booking of(String reference, int guests)` — a new `PENDING` booking
