using Learnbox;
using Lesson;

public class SignalsTests
{
    [Test]
    public void ComposeAppliesFirstThenSecond()
    {
        var f = Signals.Compose(x => x + 1, x => x * 10);
        Assert.Equal(30, f(2));
    }

    [Test]
    public void ComposeIsNotCommutative()
    {
        var other = Signals.Compose(x => x * 10, x => x + 1);
        Assert.Equal(21, other(2));
    }

    [Test]
    public void ApplyAllTransformsEveryElement() =>
        Assert.Sequence(new[] { 2, 4, 6 }, Signals.ApplyAll(new[] { 1, 2, 3 }, x => x * 2));

    [Test]
    public void ApplyAllOfNothing() =>
        Assert.Equal(0, Signals.ApplyAll(Array.Empty<int>(), x => x).Count);

    [Test]
    public void ApplyAllTakesAMethodGroupToo() =>
        Assert.Sequence(new[] { 1, 2 }, Signals.ApplyAll(new[] { -1, -2 }, Math.Abs));

    [Test]
    public void TheCounterRemembersBetweenCalls()
    {
        var next = Signals.Counter();
        Assert.Equal(1, next());
        Assert.Equal(2, next());
        Assert.Equal(3, next());
    }

    [Test]
    public void EachCounterIsIndependent()
    {
        var a = Signals.Counter();
        var b = Signals.Counter();
        a();
        a();
        Assert.Equal(1, b());
    }

    [Test]
    public void ALambdaCanBeStoredAndPassedAround()
    {
        Func<int, int> square = x => x * x;
        Assert.Sequence(new[] { 1, 4, 9 }, Signals.ApplyAll(new[] { 1, 2, 3 }, square));
    }

    [Test]
    public void TheGaugeRemembersTheLastValue()
    {
        var gauge = new Gauge(10m);
        gauge.Record(3m);
        Assert.Equal(3m, gauge.Last);
    }

    [Test]
    public void RecordingBelowTheLimitRaisesNothing()
    {
        var gauge = new Gauge(10m);
        int raised = 0;
        gauge.Threshold += (_, _) => raised++;
        gauge.Record(9m);
        gauge.Record(10m);
        Assert.Equal(0, raised);
    }

    [Test]
    public void RecordingAboveTheLimitRaises()
    {
        var gauge = new Gauge(10m);
        decimal seen = 0m;
        gauge.Threshold += (_, value) => seen = value;
        gauge.Record(11m);
        Assert.Equal(11m, seen);
    }

    [Test]
    public void EverySubscriberIsCalled()
    {
        var gauge = new Gauge(1m);
        int a = 0, b = 0;
        gauge.Threshold += (_, _) => a++;
        gauge.Threshold += (_, _) => b++;
        gauge.Record(5m);
        Assert.Equal(1, a);
        Assert.Equal(1, b);
    }

    [Test]
    public void UnsubscribingStopsTheCalls()
    {
        var gauge = new Gauge(1m);
        int count = 0;
        EventHandler<decimal> handler = (_, _) => count++;
        gauge.Threshold += handler;
        gauge.Record(5m);
        gauge.Threshold -= handler;
        gauge.Record(5m);
        Assert.Equal(1, count);
    }

    [Test]
    public void RaisingWithNoSubscribersIsFine()
    {
        // Threshold is null here; an unguarded Invoke would throw.
        var gauge = new Gauge(1m);
        gauge.Record(5m);
        Assert.Equal(5m, gauge.Last);
    }

    [Test]
    public void TheSenderIsTheGauge()
    {
        var gauge = new Gauge(1m);
        object? sender = null;
        gauge.Threshold += (s, _) => sender = s;
        gauge.Record(2m);
        Assert.True(ReferenceEquals(gauge, sender));
    }
}
