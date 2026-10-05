---
title: "Boss: The library desk"
summary: Books, members, loans and limits. Collections, Optional and the right exception for each refusal.
order: 3
files: [Library.java]
run: javac Library.java && java Library
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 1400
---

The library opens in half an hour and the lending desk has no software.

## The task

In `Library.java`, finish the `Library` class. The method signatures are
there; the bodies and the fields are yours.

### Books

- `void addBook(String isbn, String title)` adds a book. An ISBN that is
  already in the library throws `IllegalArgumentException`.
- `List<String> available()` returns the **titles** of the books that are
  not on loan, in alphabetical order.

### Lending

- `void lend(String isbn, String member)` lends a book. In this order:
  - an ISBN the library does not have throws `NoSuchElementException`
  - a book already on loan throws `IllegalStateException`
  - a member who already has `LIMIT` books (3) throws
    `IllegalStateException`
- `void giveBack(String isbn)` returns a book. An unknown ISBN throws
  `NoSuchElementException`; a book that is not on loan throws
  `IllegalStateException`.

A refused call changes nothing.

### Questions

- `Optional<String> whoHas(String isbn)` is the member who has the book, or
  empty if it is on the shelf. An unknown ISBN throws
  `NoSuchElementException`.
- `List<String> borrowedBy(String member)` returns the titles that member
  has, in alphabetical order. A member with nothing, or nobody the library
  has heard of, gets an empty list.
- `Map<String, Integer> loanCounts()` maps each member who currently has at
  least one book to how many they have.

The lists and the map you return are the caller's to keep: changing them
must not change the library.

```java
Library lib = new Library();
lib.addBook("111", "Dune");
lib.addBook("222", "Emma");
lib.lend("111", "ana");
lib.whoHas("111");        // Optional[ana]
lib.available();          // [Emma]
lib.borrowedBy("ana");    // [Dune]
lib.giveBack("111");
lib.available();          // [Dune, Emma]
```
