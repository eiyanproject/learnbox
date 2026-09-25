using Learnbox;
using Lesson;

public class WorkTests
{
    // The runner invokes void methods by reflection, so each test blocks on
    // the task itself rather than being async.
    private static T Run<T>(Func<Task<T>> work) => work().GetAwaiter().GetResult();

    [Test]
    public void DoubleAsyncReturnsTheDoubledValue() =>
        Assert.Equal(10, Run(() => Work.DoubleAsync(5)));

    [Test]
    public void DoubleAsyncOfZero() =>
        Assert.Equal(0, Run(() => Work.DoubleAsync(0)));

    [Test]
    public void SumAllAsyncAddsTheDoubledValues() =>
        Assert.Equal(12, Run(() => Work.SumAllAsync(new[] { 1, 2, 3 })));

    [Test]
    public void SumAllAsyncOfNothingIsZero() =>
        Assert.Equal(0, Run(() => Work.SumAllAsync(Array.Empty<int>())));

    [Test]
    public void SumAllAsyncRunsThemConcurrently()
    {
        // Twenty 1ms delays, sequentially, could not finish this fast. The
        // margin is wide so a loaded machine does not fail the test.
        var started = DateTime.UtcNow;
        Run(() => Work.SumAllAsync(Enumerable.Range(1, 20)));
        Assert.True((DateTime.UtcNow - started).TotalMilliseconds < 1000);
    }

    [Test]
    public void FailAsyncProducesAFaultedTask()
    {
        Task<int> task = Work.FailAsync();
        Assert.Throws<InvalidOperationException>(() => task.GetAwaiter().GetResult());
    }

    [Test]
    public void AwaitRethrowsTheOriginalException()
    {
        var result = Assert.Throws<InvalidOperationException>(
            () => Work.FailAsync().GetAwaiter().GetResult());
        Assert.Equal("boom", result.Message);
    }

    [Test]
    public void BlockingOnResultWrapsItInAnAggregateException()
    {
        // The reason .Result is a trap: the exception you catch is not the one
        // that was thrown.
        var task = Work.FailAsync();
        var aggregate = Assert.Throws<AggregateException>(() => _ = task.Result);
        Assert.True(aggregate.InnerException is InvalidOperationException);
    }

    [Test]
    public void TryRunAsyncReturnsTheValueOnSuccess() =>
        Assert.Equal(8, Run(() => Work.TryRunAsync(() => Work.DoubleAsync(4)))!.Value);

    [Test]
    public void TryRunAsyncReturnsNullOnFailure() =>
        Assert.Null(Run(() => Work.TryRunAsync(Work.FailAsync)));

    [Test]
    public void CountUpAsyncCountsToTheLimit() =>
        Assert.Equal(5, Run(() => Work.CountUpAsync(5, CancellationToken.None)));

    [Test]
    public void CountUpAsyncOfZero() =>
        Assert.Equal(0, Run(() => Work.CountUpAsync(0, CancellationToken.None)));

    [Test]
    public void AnAlreadyCancelledTokenStopsItImmediately()
    {
        using var source = new CancellationTokenSource();
        source.Cancel();
        Assert.Throws<OperationCanceledException>(
            () => Work.CountUpAsync(1000, source.Token).GetAwaiter().GetResult());
    }

    [Test]
    public void AnUncancelledTokenChangesNothing()
    {
        using var source = new CancellationTokenSource();
        Assert.Equal(3, Run(() => Work.CountUpAsync(3, source.Token)));
    }

    [Test]
    public void EveryElementIsDoubledNotJustSummed() =>
        Assert.Equal(20, Run(() => Work.SumAllAsync(new[] { 10 })));
}
