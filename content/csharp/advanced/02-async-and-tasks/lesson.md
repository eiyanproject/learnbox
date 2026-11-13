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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **`Task`** | work that will finish; `Task<T>` finishes with a value |
| **async method** | marked `async`, returns a Task, may `await` |
| **I/O** | input and output: network, disk, database |
| **thread pool** | reusable threads; a thread waiting on I/O goes back to it |
| **`Task.Run`** | moves CPU work to a pool thread |
| **`await`** | waits for a Task without blocking; the rest becomes a continuation |
| **continuation** | the code after an `await`, run when the task completes; maybe on another thread |
| **deadlock** | two things waiting for each other forever |
| **context switch** | moving work back to the original thread or context |
| **sequential** / **concurrent** | one after another / all started, then waited for |
| **`AggregateException`** | wraps one or more exceptions, from `.Wait()`, `.Result` or `WhenAll` |
| **async all the way up** | never block on a Task with `.Result` |
| **cancellation** | cooperative: your code checks a token and throws |
| **`CancellationToken`** | the object that signals cancellation |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `dotnet build -c Release` | compiles the project in Release mode |
| `dotnet bin/Release/net8.0/lesson.dll` | runs the compiled program |

### C# names

| Name | What it does |
|---|---|
| `public static async Task<int> DoubleAsync(int n)` | an async method |
| `await Task.Delay(1)` | waits without blocking |
| `await Task.WhenAll(tasks)` | waits for all; rethrows the first failure |
| `task.Exception` | every failure of a task |
| `.Result`, `.Wait()` | block on a Task; avoid |
| `ConfigureAwait(false)` | do not return to the original context |
| `token.ThrowIfCancellationRequested()` | throws if cancelled |
| `int?` | an int or null |
| `Func<Task<int>> work` | a function returning a Task |
| `e.InnerException` | the exception an `AggregateException` wraps |

### Errors

| Error | Means |
|---|---|
| `OperationCanceledException` | thrown when cancellation is requested |
| `AggregateException` | the wrapper from blocking on a failed Task |

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

The difference between `await` and `.Wait()`, seen from the `catch`:

```csharp
var results = await Task.WhenAll(new[] { 1, 2, 3 }.Select(DoubleAsync));
Console.WriteLine(string.Join(",", results));

try { await FailAsync(); }
catch (InvalidOperationException e) { Console.WriteLine($"await: {e.GetType().Name}"); }

try { FailAsync().Wait(); }
catch (AggregateException e)
{
    Console.WriteLine($"Wait: {e.GetType().Name} around {e.InnerException!.GetType().Name}");
}

static async Task<int> DoubleAsync(int n)
{
    await Task.Delay(1);
    return n * 2;
}

static async Task FailAsync()
{
    await Task.Delay(1);
    throw new InvalidOperationException("nope");
}
```

```output
2,4,6
await: InvalidOperationException
Wait: AggregateException around InvalidOperationException
```

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
