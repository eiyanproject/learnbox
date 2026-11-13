---
title: Building a small service
summary: An interface, an implementation behind it, and the dependency passed in rather than created - the shape almost every Java application has.
order: 2
files: [Library.java]
run: javac Library.java && java Library
hints:
  - "`BookStore` is the interface: `save(Book)`, `findByTitle(String)` returning Optional, and `all()`. `InMemoryStore` implements it with a LinkedHashMap keyed by title."
  - "`LibraryService` takes a BookStore in its CONSTRUCTOR - that is the dependency injection the test relies on to swap in its own store."
  - "`add` should reject a duplicate title with IllegalStateException; check `findByTitle` first."
  - "`titlesByAuthor` groups with a stream: `all().stream().collect(groupingBy(Book::author, mapping(Book::title, toList())))`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **service** | the class that holds the program's operations, here `LibraryService` |
| **store** | where data is kept: a map today, a database tomorrow |
| **interface** | says what something does, not how |
| **implementation** | a class that does it, such as `InMemoryStore` |
| **program to the interface** | declare variables and parameters with the interface type; name the class only where it is created |
| **dependency** | an object another object needs, as the service needs a store |
| **dependency injection** | passing the dependency in, usually through the constructor, instead of creating it inside |
| **welded** | hard-wired to one implementation, so it cannot be swapped or tested |
| **fake** | a stand-in implementation written for a test |
| **spy** | a fake that records the calls made to it |
| **anonymous class** | an interface implemented on the spot: `new BookStore() { ... }` |
| **layer** | one level of the program: model, store, service, caller |
| **depends downwards** | each layer knows only the ones below it |
| **leak** (between layers) | a type from one layer escaping into another's signature |
| **model** | the data types, such as `Book`; validation rules live here |
| **Spring** | a framework that automates dependency injection |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Library.java && java Library` | builds and runs this lesson's file |

### Java keywords, classes and methods

| Name | What it does |
|---|---|
| `interface BookStore { void save(Book b); Optional<Book> findByTitle(String t); List<Book> all(); }` | the store's interface |
| `class InMemoryStore implements BookStore` | the in-memory implementation |
| `LinkedHashMap` | a map that keeps insertion order, for `all()` |
| `LibraryService(BookStore store) { this.store = store; }` | constructor injection |
| `private final BookStore store;` | the injected dependency |
| `Optional<Book>` | "maybe a book", instead of `null` |
| `store.findByTitle(t).isPresent()` | is that title already stored |
| `Collectors.groupingBy(Book::author, LinkedHashMap::new, Collectors.mapping(Book::title, Collectors.toList()))` | author to titles, in insertion order |

### Errors

| Error | Means |
|---|---|
| `IllegalArgumentException` | an invalid book, such as a blank title |
| `IllegalStateException` | a duplicate title: the store already has it |

---

Real Java programs are mostly the same shape: an interface describing what
something does, a class doing it, and callers that depend on the interface
rather than the class. This lesson builds the smallest complete example: a
library that stores books and answers questions about them. It is small
enough to read in one sitting and has every part a large application has,
so the shape carries over directly.

## Program to the interface

```java
interface BookStore {
    void save(Book book);
    Optional<Book> findByTitle(String title);
    List<Book> all();
}
```

The interface says *what*, not *how*. Today the implementation is a `HashMap`;
tomorrow it is a database. Nothing that uses `BookStore` has to change, because
nothing that uses it knows which one it has. "Programming to the interface"
means declaring variables, fields and parameters with the interface type
(`BookStore store`), and naming the concrete class only at the one place an
object is created.

`findByTitle` returns `Optional<Book>` rather than a `Book` that might be
`null`, so the signature itself tells callers that a title may not be found
(the Optional lesson).

## Inject the dependency, do not create it

```java
class LibraryService {
    private final BookStore store;

    LibraryService(BookStore store) {   // handed in
        this.store = store;
    }
}
```

Compare with `this.store = new InMemoryStore();` inside the constructor. That
version is welded to one implementation and **cannot be tested** without it —
no way to substitute a fake, no way to check what the service asked the store
to do.

A **dependency** is an object another object needs in order to work: the
service needs a store. **Injecting** it means passing it in from outside,
usually through the constructor, instead of the object creating its own.
This is dependency injection, and it is the whole idea before any framework
gets involved. Spring automates the wiring; it does not change the shape.

Here is what that makes possible. A test can hand the service a store of its
own, written on the spot, that records what was asked of it:

```java
import java.util.*;

public class Injection {
    record Book(String title) {}

    interface BookStore {
        void save(Book book);
        Optional<Book> findByTitle(String title);
    }

    static class LibraryService {
        private final BookStore store;
        LibraryService(BookStore store) { this.store = store; }
        void add(Book b) { store.save(b); }
    }

    public static void main(String[] args) {
        List<String> saved = new ArrayList<>();
        BookStore spy = new BookStore() {               // a fake, made for the test
            public void save(Book book) { saved.add(book.title()); }
            public Optional<Book> findByTitle(String t) { return Optional.empty(); }
        };
        new LibraryService(spy).add(new Book("Dune"));
        System.out.println("the service saved " + saved);
    }
}
```

```output
the service saved [Dune]
```

The service never knew it was talking to a fake. A fake like this, which
records the calls made to it, is often called a **spy**. With the store
created inside the service, none of this would be possible. (`new
BookStore() { ... }` is an anonymous class, from the Lambdas lesson: an
interface implemented on the spot. A lambda cannot be used here because
`BookStore` has more than one method.)

## Keep the layers apart

| Layer | Knows about |
|---|---|
| Model (`Book`) | nothing else |
| Store | the model |
| Service | the store interface |
| Caller | the service |

Each layer depends downwards only. When a change in storage forces a change in
the model, the layering has leaked — usually because a type from one layer
escaped into another's signature. For example, if `LibraryService.find`
returned a database row object instead of a `Book`, every caller would now
depend on the database, and switching to another store would ripple through
the whole program.

Rules about what makes a valid book belong in the model, in `Book`'s own
compact constructor, not in the service. Then every book is valid, however
it was created, and the service does not have to repeat the check.

## Your turn

In `Library.java`:

All in the one file, below the public `Library` class:

- `record Book(String title, String author, int year)`, whose compact
  constructor rejects a null or blank title with `IllegalArgumentException`
- `interface BookStore` with `void save(Book)`, `Optional<Book>
  findByTitle(String)` and `List<Book> all()`
- `class InMemoryStore implements BookStore`, where `all()` returns the books
  in the order they were saved
- `class LibraryService` taking a `BookStore` in its constructor, with:
  - `add(Book)` — stores the book, but rejects a title that is already stored
    with `IllegalStateException`, without storing anything
  - `find(String)` — the book with that title, as an `Optional`, empty if
    there is none
  - `count()` — how many books are stored
  - `titlesByAuthor()` — a `Map<String, List<String>>` from each author to
    their titles, in the order the books were added; an empty map when there
    are no books

The service must use only the `BookStore` interface: a test hands it a store
of its own, like the spy above.
