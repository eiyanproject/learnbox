---
title: A log report
summary: The capstone - parse lines into records, skip the broken ones lazily, and answer questions about them with LINQ.
order: 4
files: [LogReport.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "A line is four space-separated fields: timestamp, level, service, duration. Anything else is not a log line."
  - "Use `DateTime.TryParse(parts[0], CultureInfo.InvariantCulture, DateTimeStyles.None, out var when)` so the machine's locale cannot change the answer."
  - "`ParseAll` is an iterator: `yield return` the entries that parse and simply skip the ones that do not."
  - "`Summarise` of an empty sequence is \"no entries\" - decide that before calling Max, which throws on empty."
---

Everything from this track in one place. The input is a log:

```
2026-01-02T03:04:05 ERROR api 125
2026-01-02T03:04:06 INFO  web 12
```

and the output is answers about it.

## The shape

```
lines  ->  TryParse  ->  entries  ->  LINQ  ->  answers
```

Four fields per line: timestamp, level, service, duration in milliseconds. A
line that does not fit is skipped, not fatal — logs have truncated lines, and
one bad line must not lose the other fifty thousand.

## Why each piece is what it is

**A record for the entry.** It is data with no behaviour, it should be
immutable, and value equality makes it comparable in a test without writing
`Equals`.

**`TryParse` rather than an exception.** A malformed line is a normal thing to
meet in a log file. Exceptions are for the caller's bugs, and a log file is not
one.

**An iterator for `ParseAll`.** Logs are large and often only partly consumed —
`ParseAll(lines).Take(100)` should read a hundred lines, not a million. That
falls out of `yield return` for free.

**LINQ for the questions.** `GroupBy`, `OrderByDescending`, `ToDictionary`. The
query says what is wanted; the loop would say how to get it.

## The empty case

`Max()` and `Average()` throw on an empty sequence rather than inventing a
value — there genuinely is no maximum of nothing. Decide what an empty report
says *before* you call them.

## Your turn

In `LogReport.cs`:

- `record LogEntry(DateTime When, string Level, string Service, int DurationMs)`
- `static bool TryParse(string? line, out LogEntry? entry)`
- `static IEnumerable<LogEntry> ParseAll(IEnumerable<string> lines)`
- `static Dictionary<string, int> CountByLevel(IEnumerable<LogEntry> entries)`
- `static List<string> SlowServices(IEnumerable<LogEntry> entries, int thresholdMs)`
- `static string Summarise(IEnumerable<LogEntry> entries)`
