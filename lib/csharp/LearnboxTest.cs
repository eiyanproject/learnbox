// A minimal test framework for the learnbox C# lessons.
//
// Not xunit or NUnit, because both arrive through NuGet and a check would then
// need a package restore - network access, a cache to warm, and several seconds
// per run. This is one file the runner copies in beside the lesson, so `dotnet
// build` sees no PackageReference at all and works entirely offline.
//
// It writes JUnit XML, which the runner already parses for pytest and JUnit.
//
// Usage in a lesson's test file:
//
//     public class CalcTests {
//         [Test] public void AddsTwoNumbers() => Assert.Equal(5, Calc.Add(2, 3));
//     }

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace Learnbox;

[AttributeUsage(AttributeTargets.Method)]
public sealed class TestAttribute : Attribute
{
    public string? Name { get; init; }
}

public sealed class AssertionException : Exception
{
    public AssertionException(string message) : base(message) { }
}

public static class Assert
{
    public static void True(bool condition, string? because = null)
    {
        if (!condition)
        {
            throw new AssertionException(because ?? "expected true, got false");
        }
    }

    public static void False(bool condition, string? because = null)
    {
        if (condition)
        {
            throw new AssertionException(because ?? "expected false, got true");
        }
    }

    public static void Equal<T>(T expected, T actual, string? because = null)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new AssertionException(
                $"expected {Show(expected)}, got {Show(actual)}" +
                (because is null ? "" : $" - {because}"));
        }
    }

    public static void NotEqual<T>(T expected, T actual)
    {
        if (EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new AssertionException($"expected something other than {Show(expected)}");
        }
    }

    public static void Near(double expected, double actual, double tolerance = 1e-6)
    {
        if (Math.Abs(expected - actual) > tolerance)
        {
            throw new AssertionException($"expected {expected}, got {actual}");
        }
    }

    public static void Null(object? value)
    {
        if (value is not null)
        {
            throw new AssertionException($"expected null, got {Show(value)}");
        }
    }

    public static void NotNull(object? value)
    {
        if (value is null)
        {
            throw new AssertionException("expected a value, got null");
        }
    }

    /// <summary>Runs the action and returns the exception it threw.</summary>
    public static TException Throws<TException>(Action action) where TException : Exception
    {
        try
        {
            action();
        }
        catch (TException expected)
        {
            return expected;
        }
        catch (Exception other)
        {
            throw new AssertionException(
                $"expected {typeof(TException).Name}, got {other.GetType().Name}: {other.Message}");
        }
        throw new AssertionException($"expected {typeof(TException).Name}, nothing was thrown");
    }

    public static void Sequence<T>(IEnumerable<T> expected, IEnumerable<T> actual)
    {
        var e = expected.ToList();
        var a = actual.ToList();
        if (!e.SequenceEqual(a))
        {
            throw new AssertionException($"expected [{string.Join(", ", e)}], got [{string.Join(", ", a)}]");
        }
    }

    private static string Show<T>(T value) => value switch
    {
        null => "null",
        string s => $"\"{s}\"",
        _ => value.ToString() ?? "?",
    };
}

public static class TestRunner
{
    public static int Main()
    {
        var results = new List<(string Name, string? Failure)>();

        // Every [Test] method in the assembly, sorted so a run is repeatable:
        // reflection makes no promise about order.
        var methods = Assembly.GetExecutingAssembly()
            .GetTypes()
            .SelectMany(t => t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static))
            .Where(m => m.GetCustomAttribute<TestAttribute>() is not null)
            .OrderBy(m => m.DeclaringType!.Name)
            .ThenBy(m => m.Name)
            .ToList();

        foreach (var method in methods)
        {
            var name = method.GetCustomAttribute<TestAttribute>()!.Name ?? method.Name;
            try
            {
                var instance = method.IsStatic ? null : Activator.CreateInstance(method.DeclaringType!);
                method.Invoke(instance, null);
                results.Add((name, null));
                Console.WriteLine($"ok   {name}");
            }
            catch (TargetInvocationException wrapped)
            {
                // Reflection wraps whatever the test threw; the inner one is
                // the message the learner needs to read.
                var inner = wrapped.InnerException ?? wrapped;
                var message = inner is AssertionException
                    ? inner.Message
                    : $"{inner.GetType().Name}: {inner.Message}";
                results.Add((name, message));
                Console.WriteLine($"FAIL {name}\n     {message}");
            }
        }

        var failures = results.Count(r => r.Failure is not null);
        Console.WriteLine($"\n{results.Count} tests, {failures} failed");
        WriteJUnit(results, failures);
        return failures == 0 ? 0 : 1;
    }

    private static void WriteJUnit(List<(string Name, string? Failure)> results, int failures)
    {
        var xml = new StringBuilder();
        xml.AppendLine("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        xml.AppendLine($"<testsuite name=\"learnbox\" tests=\"{results.Count}\" failures=\"{failures}\">");
        foreach (var (name, failure) in results)
        {
            xml.Append($"  <testcase classname=\"learnbox\" name=\"{Escape(name)}\"");
            if (failure is null)
            {
                xml.AppendLine("/>");
            }
            else
            {
                xml.AppendLine($"><failure message=\"{Escape(failure)}\"></failure></testcase>");
            }
        }
        xml.AppendLine("</testsuite>");
        File.WriteAllText("TEST-learnbox.xml", xml.ToString());
    }

    private static string Escape(string s) => s
        .Replace("&", "&amp;")
        .Replace("<", "&lt;")
        .Replace(">", "&gt;")
        .Replace("\"", "&quot;")
        .Replace("'", "&apos;");
}
