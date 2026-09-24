---
title: Classes, properties and records
summary: Properties instead of getters, the constructor shorthand, and the one-line record that replaces a page of boilerplate.
order: 1
files: [Account.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "`Balance` is a property with a public getter and a private setter: `public decimal Balance { get; private set; }` - readable from outside, writable only inside."
  - "Use `decimal` for money, not double: decimal is base-10 and does not lose cents to binary rounding."
  - "Throw `ArgumentOutOfRangeException` for a non-positive deposit and `InvalidOperationException` for overdrawing - the type of exception is part of the API."
  - "`Money` is a record struct or record: `public record Money(decimal Amount, string Currency);` gives equality and ToString for free."
---

A C# property looks like a field and runs like a method:

```csharp
public decimal Balance { get; private set; }
```

Readable anywhere, writable only inside the class. Compare with Java's
`getBalance()` / `setBalance()` pair: the property is the same thing with the
ceremony removed, and it can grow a body later without any caller changing.

```csharp
public decimal Balance
{
    get => _balance;
    private set => _balance = value >= 0 ? value : throw new ArgumentException();
}
```

`value` is the implicit parameter of a setter. An auto-property (`{ get; set; }`)
generates the backing field for you.

Other forms worth knowing:

- `{ get; init; }` — settable only during construction, then immutable
- `=> expression` — a computed, read-only property
- `public required string Name { get; init; }` — the compiler enforces that an
  object initialiser sets it

## Constructors

```csharp
public Account(string owner, decimal opening = 0)
{
    Owner = owner;
    Balance = opening;
}
```

Default parameter values mean one constructor often replaces three overloads.

## decimal for money

`double` is binary floating point: `0.1 + 0.2` is not `0.3`, and money
accumulates that error visibly. `decimal` is base-10 with 28 significant
digits — slower, exact for the values people care about, and the right choice
for currency every time.

## Records

```csharp
public record Money(decimal Amount, string Currency);
```

One line gives an immutable type with value equality, `GetHashCode`,
`ToString`, deconstruction, and `with` for derived copies:

```csharp
var doubled = money with { Amount = money.Amount * 2 };
```

Two `Money` values with the same fields are `==` equal, where two classes would
not be. Use a record for data, a class for something with identity and
behaviour.

## Your turn

In `Account.cs`, in `namespace Lesson`:

- `public record Money(decimal Amount, string Currency)`
- `public class Account` with `Owner` (get only), `Balance` (get, private set),
  a constructor taking owner and an optional opening balance
- `Deposit(decimal)` — `ArgumentOutOfRangeException` when not positive
- `Withdraw(decimal)` — also `InvalidOperationException` when it would overdraw
- `Money AsMoney()` returning the balance in `"EUR"`
