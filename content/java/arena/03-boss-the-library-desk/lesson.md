---
title: "Boss: The library desk"
summary: Books, members, loans and limits. Collections, Optional and the right exception for each refusal.
order: 4
files: [Library.java]
run: javac Library.java && java Library
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 1400
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **boss round** | the longest arena round, combining several lessons |
| **ISBN** | a book's unique number, used here as its key |
| **on loan** | lent to a member and not yet returned |
| **on the shelf** (available) | not on loan |
| **member** | a person who borrows books, named by a string |
| **limit** | the most books one member may have at once: `LIMIT`, 3 |
| **refused call** | one that throws; it must change nothing |
| **order of checks** | which refusal wins when several apply: unknown ISBN, then on loan, then the limit |
| **defensive copy** | returning a new list or map, so the caller's changes cannot reach inside the library |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Library.java && java Library` | builds and runs this round's file |

### Java names

| Name | What it does |
|---|---|
| `addBook`, `available`, `lend`, `giveBack` | add a book; titles on the shelf; lend; return |
| `whoHas`, `borrowedBy`, `loanCounts` | who has a book; a member's titles; members to their number of books |
| `Map<String, String>` | one way to hold ISBN to title, or ISBN to member |
| `Optional<String>`, `Optional.ofNullable(x)`, `Optional.empty()` | "maybe a member" |
| `new ArrayList<>(list)`, `new HashMap<>(map)` | defensive copies |
| `Collections.sort(list)`, `sorted()` | alphabetical order |
| `map.containsKey(k)` | is that ISBN known |

### Errors

| Error | Means |
|---|---|
| `IllegalArgumentException` | adding an ISBN that is already there |
| `NoSuchElementException` | an ISBN the library does not have |
| `IllegalStateException` | a book already on loan, one not on loan, or a member at the limit |

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
