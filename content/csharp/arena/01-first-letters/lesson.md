---
title: "Round 1: First letters"
summary: Two string puzzles that LINQ over characters makes short work of.
order: 1
files: [Words.cs]
run: dotnet build -c Release
challenge:
  minutes: 12
  xp: 150
  requires:
    xp: 100
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **acronym** | the first letter of each word, upper-cased: "PNG" |
| **isogram** | a word with no repeated letter |
| **case-insensitive** | upper and lower case count as the same |
| **static class** | a class of static methods only |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `dotnet build -c Release` | compiles the project, to check it builds |

### C# names

| Name | What it does |
|---|---|
| `phrase.Split(new[] { ' ', '-' })` | splits on spaces and hyphens |
| `char.IsLetter(c)` | true for a letter |
| `char.ToUpperInvariant(c)`, `char.ToLowerInvariant(c)` | changes case |
| `StringBuilder` | builds a string piece by piece |
| `HashSet<char>` | remembers letters already seen |

---

The glossary tool needs two helpers before the documentation build runs.

## The task

In `Words.cs`, write the two methods of the static class `Words`.

`string Acronym(string phrase)` builds an acronym: the first **letter** of
each word, upper-cased. Words are separated by spaces and by hyphens.
Anything that is not a letter is skipped over, and a piece with no letters
in it contributes nothing.

```text
Acronym("portable network graphics")                 ->  "PNG"
Acronym("Complementary metal-oxide semiconductor")   ->  "CMOS"
Acronym("  as   soon as possible ")                  ->  "ASAP"
Acronym("the 'quick' fox")                           ->  "TQF"
Acronym("")                                          ->  ""
```

`bool IsIsogram(string word)` is `true` when no letter appears more than
once. Case does not matter, and characters that are not letters - spaces,
hyphens, digits - are ignored.

```text
IsIsogram("lumberjacks")    ->  true
IsIsogram("six-year-old")   ->  true
IsIsogram("Alpha")          ->  false   (two a's)
IsIsogram("")               ->  true
```
