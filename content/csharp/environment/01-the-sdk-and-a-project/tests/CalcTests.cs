using Learnbox;
using Lesson;

public class CalcTests
{
    [Test]
    public void AddsTwoNumbers() => Assert.Equal(5, Calc.Add(2, 3));

    [Test]
    public void AddsNegatives() => Assert.Equal(-1, Calc.Add(2, -3));

    [Test]
    public void DescribesNegative() => Assert.Equal("negative", Calc.Describe(-5));

    [Test]
    public void DescribesZero() => Assert.Equal("zero", Calc.Describe(0));

    [Test]
    public void DescribesPositive() => Assert.Equal("positive", Calc.Describe(7));

    [Test]
    public void AveragesWithoutTruncating() =>
        Assert.Near(4.5, Calc.Average(new[] { 4, 5 }));

    [Test]
    public void AveragesSeveralValues() =>
        Assert.Near(2.0, Calc.Average(new[] { 1, 2, 3 }));

    [Test]
    public void AverageOfEmptyIsZero() =>
        Assert.Near(0, Calc.Average(Array.Empty<int>()));

    [Test]
    public void RepeatsText() => Assert.Equal("abab", Calc.Repeat("ab", 2));

    [Test]
    public void RepeatZeroTimesIsEmpty() => Assert.Equal("", Calc.Repeat("ab", 0));

    [Test]
    public void RepeatRejectsNegativeCounts() =>
        Assert.Throws<ArgumentOutOfRangeException>(() => Calc.Repeat("ab", -1));
}
