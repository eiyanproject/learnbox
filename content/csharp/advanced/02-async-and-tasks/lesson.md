---
title: async and await
summary: A Task is work in flight, not a thread. await, WhenAll, how exceptions travel, and why .Result is a trap.
order: 2
files: [Work.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "An async method returning a value is `async Task<T>`, and `return n * 2;` inside it produces the Task."
  - "`SumAllAsync` should start every task first and then `await Task.WhenAll(tasks)` - awaiting inside the loop makes them run one after another."
  - "`TryRunAsync` awaits inside a try/catch. An awaited task rethrows the original exception, so `catch (InvalidOperationException)` works directly."
  - "`CountUpAsync` calls `token.ThrowIfCancellationRequested()` each iteration; an already-cancelled token throws on the first one."
---

```csharp
public static async Task<int> DoubleAsync(int n)
{
    await Task.Delay(1);
    return n * 2;
}
```

## A Task is not a thread

A `Task` represents *work that will finish*. For genuine I/O — a socket, a
disk, a database — no thread is waiting at all: the operating system holds the
request, and the thread goes back to the pool to do something else. This is why
`async` scales a server. It is not about going faster; it is about not holding
a thread hostage while nothing happens.

`Task.Run` is the different case: CPU work moved to a pool thread. Use it for
computation, not for I/O.

## What await does

`await` splits the method in two. Everything after it becomes a continuation
that runs when the task completes; the method returns to its caller at the
first `await` that has not already finished.

The consequence to internalise: **the code after an `await` may run on a
different thread.** In a library, `ConfigureAwait(false)` says you do not care
which — it avoids deadlocks and saves a context switch.

## Concurrency needs WhenAll

```csharp
foreach (var n in values)
    total += await DoubleAsync(n);       // sequential - each waits for the last

var tasks = values.Select(DoubleAsync).ToList();
var results = await Task.WhenAll(tasks); // concurrent - all start, then wait
```

Both are async. Only the second is concurrent. Awaiting inside a loop is the
most common performance mistake in async code, and it is invisible unless you
look for it.

## Exceptions

An exception inside an async method is captured in the returned Task and
rethrown at the `await`:

```csharp
try { await FailAsync(); }
catch (InvalidOperationException) { }   // the original exception
```

Block on `.Result` or `.Wait()` instead and you get an **`AggregateException`**
wrapping it — and in a UI or old ASP.NET context, a deadlock. The rule is
async all the way up; `.Result` is for a program's entry point, if anywhere.

`Task.WhenAll` gathers every failure into an `AggregateException`, but
`await`ing it rethrows only the first. Check `task.Exception` for all of them.

## Cancellation

```csharp
token.ThrowIfCancellationRequested();
```

Cancellation is cooperative. Nothing interrupts your code; you check, and
throw. Pass the `CancellationToken` down to everything you call — a method that
accepts one and ignores it is worse than one that does not accept it.

## Your turn

In `Work.cs`:

- `static async Task<int> DoubleAsync(int n)`
- `static async Task<int> SumAllAsync(IEnumerable<int> values)` — concurrent
- `static async Task<int> FailAsync()` — throws `InvalidOperationException`
- `static async Task<int?> TryRunAsync(Func<Task<int>> work)`
- `static async Task<int> CountUpAsync(int upTo, CancellationToken token)`
