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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **property** | looks like a field, runs like a method |
| **field** | a variable stored in an object; private ones are often written `_balance` |
| **getter** / **setter** | `get` reads, `set` writes |
| **`private set`** | writable only inside the class |
| **auto-property** | `{ get; set; }`: the backing field is generated |
| **backing field** | the hidden variable a property stores its value in |
| **`value`** | the implicit parameter of a setter |
| **`init`** | settable only while the object is being created |
| **computed property** | `=> expression`: read-only, worked out each time |
| **`required`** | an object initialiser must set this property |
| **object initialiser** | `new Account { Owner = "a" }` |
| **constructor** | runs when an object is created |
| **default parameter value** | `decimal opening = 0`: used if the caller gives none |
| **overload** | several methods with the same name, different parameters |
| **`double`** | binary floating point: `0.1 + 0.2` is not exactly `0.3` |
| **`decimal`** | base-10, 28 significant digits: right for money |
| **value equality** | two records with the same fields are `==` |
| **identity** | a class object is itself, whatever its fields |
| **`with`** | a copy with some properties changed |
| **deconstruction** | splitting a record into its parts |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `dotnet build -c Release` | compiles the project in Release mode |
| `dotnet bin/Release/net8.0/lesson.dll` | runs the compiled program |

### C# names

| Name | What it does |
|---|---|
| `public decimal Balance { get; private set; }` | readable anywhere, writable inside |
| `get => _balance;` | a getter with a body |
| `cond ? a : throw new ArgumentException()` | a value, or an error |
| `public record Money(decimal Amount, string Currency);` | an immutable data type |
| `money with { Amount = money.Amount * 2 }` | a changed copy |
| `2.50m` | a `decimal` literal |
| `ArgumentOutOfRangeException`, `InvalidOperationException` | a bad argument / wrong state, such as overdrawing |

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
behaviour. Both claims from this lesson, run:

```csharp
Console.WriteLine(0.1 + 0.2 == 0.3);       // double: binary, slightly off
Console.WriteLine(0.1m + 0.2m == 0.3m);    // decimal: exact

var money = new Money(2.50m, "EUR");
var doubled = money with { Amount = money.Amount * 2 };
Console.WriteLine(doubled);
Console.WriteLine(money == new Money(2.50m, "EUR"));

record Money(decimal Amount, string Currency);
```

```output
False
True
Money { Amount = 5.00, Currency = EUR }
True
```

## Your turn

In `Account.cs`, in `namespace Lesson`:

- `public record Money(decimal Amount, string Currency)`
- `public class Account` with `Owner` (get only), `Balance` (get, private set),
  a constructor taking owner and an optional opening balance
- `Deposit(decimal)` — `ArgumentOutOfRangeException` when not positive
- `Withdraw(decimal)` — also `InvalidOperationException` when it would overdraw
- `Money AsMoney()` returning the balance in `"EUR"`
