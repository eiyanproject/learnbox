---
title: Null, and when to throw
summary: Nullable reference types, the operators that go with them, and the line between an ordinary failure and an exception.
order: 3
files: [Safety.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "With `<Nullable>enable</Nullable>`, `string` cannot be null and `string?` can. The difference is checked by the compiler, not at run time."
  - "`text?.Trim()` gives null when text is null; `?? \"\"` supplies a fallback. Chain them: `text?.Trim() ?? \"\"`."
  - "`TryParseAge` returns false and sets `age = 0` for anything that is not a number in 0..150 - bad user input is not exceptional."
  - "`Withdraw` throws: an overdraft is a broken invariant the caller cannot shrug off. Use ArgumentOutOfRangeException and InvalidOperationException."
---

## Nullable reference types

```xml
<Nullable>enable</Nullable>
```

With this on, `string` means *never null* and `string?` means *may be null*.
The compiler tracks which is which and warns when you dereference something
that might not be there.

It is **compile-time only**. Nothing is checked at run time, and a `string`
handed to you by an old library or by deserialisation can still be null. The
warnings are a very good static check, not a guarantee.

## The operators

```csharp
text?.Trim()          // null in, null out - no exception
name ?? "anonymous"   // the left unless it is null
cache ??= Build()     // assign only if currently null
value!                // "I know it is not null" - suppresses the warning
```

`!` is worth being suspicious of. It silences the compiler without changing
anything; if you are wrong you get a `NullReferenceException` exactly as
before. Use it where you know something the compiler cannot, and not to make a
warning go away.

## Which failure is which

The rule that holds up: **is this a normal outcome of correct code?**

User typed letters into an age box — normal. A file that might not exist —
normal. A lookup that misses — normal. All of these get a `bool`, a `T?`, or
the Try pattern.

A negative withdrawal, an overdraft, a null argument where one is required —
these mean the caller has a bug, or a rule has been broken. Throw. An
exception cannot be ignored, and that is precisely the point.

```csharp
if (amount <= 0) throw new ArgumentOutOfRangeException(nameof(amount));
if (amount > _balance) throw new InvalidOperationException("insufficient funds");
```

Use `nameof` rather than a string literal: rename the parameter and the message
follows.

## Which exception

| | |
|---|---|
| A bad argument value | `ArgumentException` family |
| Null where one is required | `ArgumentNullException` |
| Wrong state for this call | `InvalidOperationException` |
| Never going to be written | `NotImplementedException` |

Do not catch `Exception` to keep going. Catch what you can actually handle,
and let the rest travel.

## Your turn

In `Safety.cs`:

- `static string Display(string? name)` — trimmed, or `"anonymous"`
- `static int Length(string? text)` — 0 for null
- `static bool TryParseAge(string? text, out int age)` — 0..150
- `class Account` with `Balance`, `Deposit`, `Withdraw`
