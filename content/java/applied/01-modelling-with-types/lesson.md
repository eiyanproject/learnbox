---
title: Modelling a domain with types
summary: Making illegal states unrepresentable - records for data, enums for closed sets, and validation in the constructor rather than everywhere else.
order: 1
files: [Booking.java]
run: javac Booking.java && java Booking
hints:
  - "`Status` is an enum with PENDING, CONFIRMED and CANCELLED. An enum can hold fields and methods - give it `boolean isFinal()` returning true for CANCELLED."
  - "`Reservation` is a record with a compact constructor that validates: `Reservation { if (guests < 1) throw ... }` - no parameter list, no assignments."
  - "`confirm()` returns a NEW Reservation with the status changed, because a record is immutable. `new Reservation(reference, guests, Status.CONFIRMED)`."
  - "Reject a null or blank reference too - `reference == null || reference.isBlank()`."
---

The certification tracks teach the language. This one is about using it: the
first job in any real program is deciding what the types are.

The goal is a design where **wrong states cannot be built**. Every check you
put in the constructor is a check the rest of the program never has to repeat.
Compare the alternative, a booking stored as a few loose variables: a
`String status` and an `int guests`. Nothing stops `status = "confrimed"` or
`guests = -3`, so every method that uses them has to check them again, and
the one that forgets is where the bug appears. This lesson builds a booking
where those values simply cannot exist.

## Enums for closed sets

A booking is pending, confirmed or cancelled. Three states, known in advance:

```java
enum Status { PENDING, CONFIRMED, CANCELLED }
```

An **enum** (enumeration) is a type with a fixed list of possible values, its
**constants**, written in capitals. A variable of type `Status` can only ever
hold `Status.PENDING`, `Status.CONFIRMED`, `Status.CANCELLED`, or `null`.

Not a `String`, which admits `"confrimed"`. Not an `int`, which admits 47. The
compiler now checks every use (`Status.CONFRIMED` is a compile error),
`switch` can be exhaustive without a `default`, and the set of possibilities
is written down in one place.

Enums are full classes: they can hold fields, constructors and methods, which
is how behaviour that varies by case lives with the case rather than in a
`switch` somewhere else. A method in an enum is called on a constant, and
`this` is that constant:

```java
enum Status {
    PENDING, CONFIRMED, CANCELLED;      // the semicolon ends the list of constants

    boolean isActive() { return this != CANCELLED; }
}
```

(A sketch.) `Status.PENDING.isActive()` is `true`. Enum constants are single,
shared objects, so comparing them with `==` (or `!=`) is correct and normal,
unlike strings.

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
further checking. Every way of creating a record goes through its canonical
constructor (the one taking every component), so the check also covers
helper methods such as `confirm()` below and any static factory you add.

## Changing immutable data

You do not. You derive a new value:

```java
Booking confirm() { return new Booking(reference, guests, Status.CONFIRMED); }
```

(A method inside the record, so `reference` and `guests` are this booking's
own components.) That looks wasteful and almost never is: a small object is
cheap to create. What it buys is that no other part of the program can change
a booking behind your back — the single largest source of "how did it get
into that state" bugs. It is the same idea as `String.toUpperCase()` and
`LocalDate.plusDays()` returning new values.

## Fail fast

Validate at the boundary, throw immediately, and name what was wrong. A
constructor that accepts nonsense pushes the failure somewhere far away, where
the stack trace no longer points at the cause. "At least one guest" in the
exception's message tells whoever reads the log exactly which rule was
broken.

A **static factory** is a static method that creates an object, as an
alternative to calling the constructor directly: `of(reference, guests)` can
fill in the starting status, so callers cannot forget it or pick the wrong
one. `List.of` and `LocalDate.of` are factories in the standard library.

## Run

```java
public class Bookings {
    enum Status { PENDING, CONFIRMED, CANCELLED }

    record Booking(String reference, int guests, Status status) {
        Booking {
            if (guests < 1) throw new IllegalArgumentException("at least one guest");
        }

        Booking confirm() { return new Booking(reference, guests, Status.CONFIRMED); }
    }

    public static void main(String[] args) {
        Booking b = new Booking("R1", 2, Status.PENDING);
        Booking c = b.confirm();
        System.out.println(b.status() + " -> " + c.status());
        System.out.println(c);
        try {
            new Booking("R2", 0, Status.PENDING);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
    }
}
```

```output
PENDING -> CONFIRMED
Booking[reference=R1, guests=2, status=CONFIRMED]
rejected: at least one guest
```

`confirm()` returned a new booking and left `b` as it was, so `b` is still
`PENDING`. The record printed itself with its generated `toString`. And the
zero-guest booking never existed: the compact constructor threw before it
could be created.

## Your turn

In `Booking.java`, the file's public class is already called `Booking` (it
only holds `main`), so the record gets a different name, `Reservation`.
Write the enum and the record **below** the `Booking` class, in the same file,
with no access modifier:

- `enum Status { PENDING, CONFIRMED, CANCELLED }` with
  `public boolean isFinal()` — true only for `CANCELLED`
- `record Reservation(String reference, int guests, Status status)` validating,
  in a compact constructor, that the reference is not null or blank (only
  spaces counts as blank) and that guests is at least 1, throwing
  `IllegalArgumentException` otherwise. The check must apply to
  `new Reservation(...)` too, not only to `of`.
- `Reservation confirm()` and `Reservation cancel()` returning new
  reservations with the status changed and the other fields kept
- `static Reservation of(String reference, int guests)` — a new `PENDING`
  reservation

Two reservations with the same reference, guests and status are equal, which
the record gives you for free.
