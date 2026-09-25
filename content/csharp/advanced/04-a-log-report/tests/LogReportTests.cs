using Learnbox;
using Lesson;

public class LogReportTests
{
    private static readonly string[] Lines =
    {
        "2026-01-02T03:04:05 ERROR api 125",
        "2026-01-02T03:04:06 INFO web 12",
        "truncated line",
        "2026-01-02T03:04:07 ERROR api 900",
        "2026-01-02T03:04:08 INFO api 8",
        "",
    };

    private static List<LogEntry> Parsed() => LogReport.ParseAll(Lines).ToList();

    [Test]
    public void TryParseReadsAGoodLine()
    {
        Assert.True(LogReport.TryParse("2026-01-02T03:04:05 ERROR api 125", out var entry));
        Assert.Equal("ERROR", entry!.Level);
        Assert.Equal("api", entry.Service);
        Assert.Equal(125, entry.DurationMs);
        Assert.Equal(2026, entry.When.Year);
    }

    [Test]
    public void TryParseUppercasesTheLevel()
    {
        Assert.True(LogReport.TryParse("2026-01-02T03:04:05 warn api 1", out var entry));
        Assert.Equal("WARN", entry!.Level);
    }

    [Test]
    public void TryParseRejectsTheWrongNumberOfFields()
    {
        Assert.False(LogReport.TryParse("2026-01-02T03:04:05 ERROR api", out var entry));
        Assert.Null(entry);
        Assert.False(LogReport.TryParse("a b c d e", out _));
    }

    [Test]
    public void TryParseRejectsABadTimestamp() =>
        Assert.False(LogReport.TryParse("not-a-date ERROR api 1", out _));

    [Test]
    public void TryParseRejectsABadDuration()
    {
        Assert.False(LogReport.TryParse("2026-01-02T03:04:05 ERROR api fast", out _));
        Assert.False(LogReport.TryParse("2026-01-02T03:04:05 ERROR api -5", out _));
    }

    [Test]
    public void TryParseRejectsNullAndBlank()
    {
        Assert.False(LogReport.TryParse(null, out _));
        Assert.False(LogReport.TryParse("   ", out _));
    }

    [Test]
    public void ParseAllSkipsTheBrokenLines() => Assert.Equal(4, Parsed().Count);

    [Test]
    public void ParseAllKeepsTheOrder() =>
        Assert.Sequence(new[] { 125, 12, 900, 8 }, Parsed().Select(e => e.DurationMs));

    [Test]
    public void ParseAllOfNothing() =>
        Assert.Equal(0, LogReport.ParseAll(Array.Empty<string>()).Count());

    [Test]
    public void ParseAllIsLazy()
    {
        // Take(1) must not force the whole sequence - an infinite source proves it.
        IEnumerable<string> Forever()
        {
            while (true)
            {
                yield return "2026-01-02T03:04:05 INFO api 1";
            }
        }
        Assert.Equal(1, LogReport.ParseAll(Forever()).Take(1).Count());
    }

    [Test]
    public void CountByLevelGroups()
    {
        var counts = LogReport.CountByLevel(Parsed());
        Assert.Equal(2, counts["ERROR"]);
        Assert.Equal(2, counts["INFO"]);
        Assert.Equal(2, counts.Count);
    }

    [Test]
    public void CountByLevelOfNothingIsEmpty() =>
        Assert.Equal(0, LogReport.CountByLevel(new List<LogEntry>()).Count);

    [Test]
    public void SlowServicesUsesTheWorstEntryPerService() =>
        Assert.Sequence(new[] { "api" }, LogReport.SlowServices(Parsed(), 100));

    [Test]
    public void SlowServicesExcludesEverythingBelowTheThreshold() =>
        Assert.Equal(0, LogReport.SlowServices(Parsed(), 1000).Count);

    [Test]
    public void SlowServicesOrdersSlowestFirst()
    {
        var entries = LogReport.ParseAll(new[]
        {
            "2026-01-02T03:04:05 INFO slow 500",
            "2026-01-02T03:04:05 INFO slower 800",
            "2026-01-02T03:04:05 INFO fine 5",
        });
        Assert.Sequence(new[] { "slower", "slow" }, LogReport.SlowServices(entries, 100));
    }

    [Test]
    public void SummariseCountsAndNamesTheSlowest() =>
        Assert.Equal("4 entries, 2 errors, slowest api at 900ms", LogReport.Summarise(Parsed()));

    [Test]
    public void SummariseOfNothing() =>
        Assert.Equal("no entries", LogReport.Summarise(new List<LogEntry>()));

    [Test]
    public void SummariseOfOneEntry() =>
        Assert.Equal("1 entries, 0 errors, slowest web at 12ms",
                     LogReport.Summarise(LogReport.ParseAll(new[] { Lines[1] })));

    [Test]
    public void EntriesCompareByValue() =>
        Assert.Equal(new LogEntry(new DateTime(2026, 1, 2), "INFO", "api", 1),
                     new LogEntry(new DateTime(2026, 1, 2), "INFO", "api", 1));
}
