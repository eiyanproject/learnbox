---
title: The SDK, a project and the CLR
summary: What dotnet build actually produces, why a .csproj exists, and the managed runtime underneath it all.
order: 1
files: [Calc.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "Put the class in `namespace Lesson;` - a file-scoped namespace declaration, which is the modern form and saves a level of indentation."
  - "`Describe` uses a switch expression: `n switch { < 0 => \"negative\", 0 => \"zero\", _ => \"positive\" }`."
  - "`Average` must not do integer division - cast to double, or divide by `values.Length` after summing into a double."
  - "`Repeat` should throw ArgumentOutOfRangeException for a negative count, and return \"\" for zero."
---

C# compiles to **IL** — an intermediate language — which the CLR then compiles
to machine code as it runs. That is the same shape as Java, and it is why a
`.dll` here is not a native library.

```bash
dotnet build -c Release          # source -> bin/Release/net8.0/lesson.dll
dotnet bin/Release/net8.0/lesson.dll
```

## The project file

A `.csproj` describes the build: which framework, which files, which packages.
The modern SDK-style one is short because everything has a default:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
```

Every `.cs` file beside it is compiled — no file list to maintain. Two settings
are worth knowing:

- **`ImplicitUsings`** adds the usual `using System;` lines for you, which is
  why short examples need no imports.
- **`Nullable`** turns on nullable reference types, so the compiler warns when
  something that might be `null` is used as if it could not be. `string?` means
  "might be null"; `string` means "should not be".

## The type system

Two families, and the split matters:

| | Examples | Stored | Assignment |
|---|---|---|---|
| **Value types** | `int`, `double`, `bool`, `struct`, `enum` | inline | copies the value |
| **Reference types** | `class`, `string`, arrays, `record` | on the heap | copies the reference |

`string` is a reference type but behaves like a value: it is immutable, and
`==` is overloaded to compare contents. That is the exception people
generalise from, wrongly.

## Modern syntax worth using immediately

```csharp
namespace Lesson;                              // file-scoped, no braces

public record Point(int X, int Y);             // immutable data

var label = n switch {                          // switch expression
    < 0 => "negative",
    0 => "zero",
    _ => "positive",
};

public static int Add(int a, int b) => a + b;  // expression-bodied member
```

## Your turn

In `Calc.cs`, a `public static class Calc` in `namespace Lesson`:

- `Add(int a, int b)`
- `Describe(int n)` — `"negative"`, `"zero"` or `"positive"`, as a switch
  expression
- `Average(int[] values)` — a `double`, `0` for an empty array
- `Repeat(string text, int count)` — repeated, `""` for zero, and
  `ArgumentOutOfRangeException` for a negative count
