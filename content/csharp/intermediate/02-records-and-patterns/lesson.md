---
title: Records and pattern matching
summary: Immutable data with value equality, and a switch that matches shape, type and condition rather than a single constant.
order: 2
files: [Figures.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "`public abstract record Shape;` - a record with no members at all still needs the semicolon."
  - "A switch expression returns a value: `s switch { Circle c => ..., Rect r => ..., _ => throw new ArgumentException(...) }`."
  - "Property patterns look inside: `Rect { Width: var w, Height: var h } when w == h`. Order matters - the first match wins."
  - "`with` copies and changes: `original with { Height = 5 }` leaves the original untouched."
---

## Records

```csharp
public record Item(int Id, string Name);
```

One line gives you a constructor, read-only properties, value-based `Equals`
and `GetHashCode`, a readable `ToString`, a `Deconstruct`, and `with`.

**Value equality** is the point. Two records with equal contents are equal,
where two classes with equal contents are not:

```csharp
new Item(1, "a") == new Item(1, "a")   // true for a record, false for a class
```

`record struct` exists too, for a value type with the same conveniences.

## with

```csharp
var taller = rect with { Height = 10 };
```

A shallow copy with some members replaced. The original is untouched, which is
what makes records comfortable to pass around — nobody can change one behind
your back.

Note *shallow*: a `List<T>` inside a record is shared by the copy.

## Switch expressions

```csharp
double Area(Shape s) => s switch
{
    Circle c => Math.PI * c.Radius * c.Radius,
    Rect r   => r.Width * r.Height,
    _        => throw new ArgumentException("unknown shape"),
};
```

An expression, not a statement: it produces a value, so it can be the whole
body of a method. No `break`, no fallthrough, and the compiler warns when the
cases are not exhaustive.

## The patterns

| | |
|---|---|
| Type | `Circle c` |
| Constant | `0`, `"north"` |
| Relational | `< 0`, `>= 100` |
| Logical | `> 0 and < 10`, `not null` |
| Property | `Rect { Width: 0 }` |
| Positional | `Rect(var w, var h)` |
| `when` guard | `Rect r when r.Width == r.Height` |

**The first match wins**, so order from specific to general. A `_` at the end
catches the rest — and if a case is unreachable because an earlier one already
covers it, the compiler says so.

## Your turn

In `Figures.cs`:

- `abstract record Shape`, with `Circle(double Radius)` and
  `Rect(double Width, double Height)`
- `static double Area(Shape s)`
- `static string Classify(Shape s)` — `"circle"`, `"square"`, `"rectangle"`
- `static string Band(int n)` — `"negative"`, `"zero"`, `"small"` (1-9),
  `"large"`
- `static Rect Grow(Rect r, double factor)` — using `with`
