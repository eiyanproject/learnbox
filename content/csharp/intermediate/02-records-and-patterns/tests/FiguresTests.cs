using Learnbox;
using Lesson;

public class FiguresTests
{
    [Test]
    public void AreaOfACircle() => Assert.Near(Math.PI * 4, Figures.Area(new Circle(2)));

    [Test]
    public void AreaOfARectangle() => Assert.Near(12, Figures.Area(new Rect(3, 4)));

    [Test]
    public void AreaOfADegenerateShape() => Assert.Near(0, Figures.Area(new Rect(0, 5)));

    [Test]
    public void ClassifyPicksTheCircle() => Assert.Equal("circle", Figures.Classify(new Circle(1)));

    [Test]
    public void ClassifySpotsASquareBeforeTheGeneralRectangle() =>
        Assert.Equal("square", Figures.Classify(new Rect(3, 3)));

    [Test]
    public void ClassifyFallsThroughToRectangle() =>
        Assert.Equal("rectangle", Figures.Classify(new Rect(3, 4)));

    [Test]
    public void BandCoversEveryRange()
    {
        Assert.Equal("negative", Figures.Band(-1));
        Assert.Equal("zero", Figures.Band(0));
        Assert.Equal("small", Figures.Band(1));
        Assert.Equal("small", Figures.Band(9));
        Assert.Equal("large", Figures.Band(10));
    }

    [Test]
    public void RecordsCompareByValue() =>
        Assert.Equal(new Rect(2, 3), new Rect(2, 3));

    [Test]
    public void DifferentValuesAreNotEqual() =>
        Assert.NotEqual(new Rect(2, 3), new Rect(3, 2));

    [Test]
    public void EqualRecordsHashTheSame() =>
        Assert.Equal(new Circle(1.5).GetHashCode(), new Circle(1.5).GetHashCode());

    [Test]
    public void GrowProducesANewRectangle()
    {
        var grown = Figures.Grow(new Rect(2, 3), 2);
        Assert.Near(4, grown.Width);
        Assert.Near(6, grown.Height);
    }

    [Test]
    public void GrowLeavesTheOriginalAlone()
    {
        var original = new Rect(2, 3);
        Figures.Grow(original, 10);
        Assert.Near(2, original.Width);
    }

    [Test]
    public void RecordsDeconstruct()
    {
        var (w, h) = new Rect(5, 6);
        Assert.Near(5, w);
        Assert.Near(6, h);
    }

    [Test]
    public void ToStringShowsTheContents() =>
        Assert.True(new Circle(1).ToString()!.Contains("Radius"));
}
