using System.Globalization;

namespace Lesson;

public record LogEntry(DateTime When, string Level, string Service, int DurationMs);

public static class LogReport
{
    /// <summary>"2026-01-02T03:04:05 ERROR api 125" - anything else fails.</summary>
    public static bool TryParse(string? line, out LogEntry? entry)
    {
        entry = null;
        if (string.IsNullOrWhiteSpace(line))
        {
            return false;
        }

        string[] parts = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length != 4)
        {
            return false;
        }

        // InvariantCulture so the machine's locale cannot change the answer.
        if (!DateTime.TryParse(parts[0], CultureInfo.InvariantCulture,
                               DateTimeStyles.None, out DateTime when))
        {
            return false;
        }
        if (!int.TryParse(parts[3], NumberStyles.Integer, CultureInfo.InvariantCulture,
                          out int duration) || duration < 0)
        {
            return false;
        }

        entry = new LogEntry(when, parts[1].ToUpperInvariant(), parts[2], duration);
        return true;
    }

    // An iterator, so ParseAll(lines).Take(100) reads a hundred lines rather
    // than the whole file. A broken line is skipped, not fatal.
    public static IEnumerable<LogEntry> ParseAll(IEnumerable<string> lines)
    {
        foreach (string line in lines)
        {
            if (TryParse(line, out LogEntry? entry))
            {
                yield return entry!;
            }
        }
    }

    public static Dictionary<string, int> CountByLevel(IEnumerable<LogEntry> entries) =>
        entries.GroupBy(e => e.Level)
               .ToDictionary(g => g.Key, g => g.Count());

    /// <summary>Services whose slowest entry exceeds the threshold, slowest first.</summary>
    public static List<string> SlowServices(IEnumerable<LogEntry> entries, int thresholdMs) =>
        entries.GroupBy(e => e.Service)
               .Select(g => new { Service = g.Key, Worst = g.Max(e => e.DurationMs) })
               .Where(x => x.Worst > thresholdMs)
               .OrderByDescending(x => x.Worst)
               .ThenBy(x => x.Service, StringComparer.Ordinal)
               .Select(x => x.Service)
               .ToList();

    public static string Summarise(IEnumerable<LogEntry> entries)
    {
        List<LogEntry> all = entries.ToList();
        // Max throws on an empty sequence rather than inventing a value, so
        // the empty case is decided first.
        if (all.Count == 0)
        {
            return "no entries";
        }
        int errors = all.Count(e => e.Level == "ERROR");
        LogEntry slowest = all.OrderByDescending(e => e.DurationMs)
                              .ThenBy(e => e.Service, StringComparer.Ordinal)
                              .First();
        return $"{all.Count} entries, {errors} errors, " +
               $"slowest {slowest.Service} at {slowest.DurationMs}ms";
    }
}
