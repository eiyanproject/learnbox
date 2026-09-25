using Learnbox;
using Lesson;

public class SequencesTests
{
    [Test]
    public void EvensFilters() =>
        Assert.Sequence(new[] { 2, 4 }, Sequences.Evens(new[] { 1, 2, 3, 4, 5 }));

    [Test]
    public void EvensOfNothing() =>
        Assert.Equal(0, Sequences.Evens(Array.Empty<int>()).Count());

    [Test]
    public void EvensOfAllOdds() =>
        Assert.Equal(0, Sequences.Evens(new[] { 1, 3 }).Count());

    [Test]
    public void NaturalsStartsAtOne() =>
        Assert.Sequence(new[] { 1, 2, 3 }, Sequences.Naturals().Take(3));

    [Test]
    public void NaturalsIsInfiniteButTakeStopsIt() =>
        Assert.Equal(500500, Sequences.Naturals().Take(1000).Sum());

    [Test]
    public void NaturalsRestartsEachTimeItIsEnumerated()
    {
        var naturals = Sequences.Naturals();
        Assert.Equal(1, naturals.First());
        Assert.Equal(1, naturals.First());
    }

    [Test]
    public void TakeUntilStopsBeforeTheMatch() =>
        Assert.Sequence(new[] { 1, 2 }, Sequences.TakeUntil(new[] { 1, 2, 9, 3 }, n => n > 5));

    [Test]
    public void TakeUntilCanStopImmediately() =>
        Assert.Equal(0, Sequences.TakeUntil(new[] { 9, 1 }, n => n > 5).Count());

    [Test]
    public void TakeUntilTakesEverythingWhenNothingMatches() =>
        Assert.Sequence(new[] { 1, 2 }, Sequences.TakeUntil(new[] { 1, 2 }, n => n > 5));

    [Test]
    public void TakeUntilIsGeneric() =>
        Assert.Sequence(new[] { "a" }, Sequences.TakeUntil(new[] { "a", "stop", "b" }, s => s == "stop"));

    [Test]
    public void BuildingTheQueryProducesNothing()
    {
        var counted = new Counted(new[] { 1, 2, 3, 4 });
        var query = counted.Where(n => n > 1).Select(n => n * 10);
        Assert.NotNull(query);
        Assert.Equal(0, counted.Produced);
    }

    [Test]
    public void EnumeratingIsWhatRunsIt()
    {
        var counted = new Counted(new[] { 1, 2, 3, 4 });
        counted.Where(n => n > 1).ToList();
        Assert.Equal(4, counted.Produced);
    }

    [Test]
    public void TakeStopsTheSourceEarly()
    {
        // The pipeline pulls one element at a time, so the source is never
        // asked for the elements past the second.
        var counted = new Counted(new[] { 1, 2, 3, 4 });
        counted.Take(2).ToList();
        Assert.Equal(2, counted.Produced);
    }

    [Test]
    public void FirstStopsAfterOne()
    {
        var counted = new Counted(new[] { 1, 2, 3, 4 });
        Assert.Equal(1, counted.First());
        Assert.Equal(1, counted.Produced);
    }

    [Test]
    public void EnumeratingTwiceDoesTheWorkTwice()
    {
        var counted = new Counted(new[] { 1, 2 });
        counted.ToList();
        counted.ToList();
        Assert.Equal(4, counted.Produced);
    }

    [Test]
    public void TheWrapperIsAProperEnumerable()
    {
        var total = 0;
        foreach (int n in new Counted(new[] { 1, 2, 3 }))
        {
            total += n;
        }
        Assert.Equal(6, total);
    }
}
