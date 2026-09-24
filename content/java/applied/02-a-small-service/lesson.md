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

Real Java programs are mostly the same shape: an interface describing what
something does, a class doing it, and callers that depend on the interface
rather than the class.

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
nothing that uses it knows which one it has.

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

This is dependency injection, and it is the whole idea before any framework
gets involved. Spring automates the wiring; it does not change the shape.

## Keep the layers apart

| Layer | Knows about |
|---|---|
| Model (`Book`) | nothing else |
| Store | the model |
| Service | the store interface |
| Caller | the service |

Each layer depends downwards only. When a change in storage forces a change in
the model, the layering has leaked — usually because a type from one layer
escaped into another's signature.

## Your turn

In `Library.java`:

- `record Book(String title, String author, int year)`
- `interface BookStore` with `save`, `findByTitle` (returning `Optional<Book>`)
  and `all`
- `class InMemoryStore implements BookStore` preserving insertion order
- `class LibraryService` taking a `BookStore` in its constructor, with
  `add(Book)` rejecting duplicate titles with `IllegalStateException`,
  `find(String)`, `count()`, and
  `titlesByAuthor()` returning `Map<String, List<String>>`
