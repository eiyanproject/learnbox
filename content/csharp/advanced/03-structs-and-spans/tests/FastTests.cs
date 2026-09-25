using Learnbox;
using Lesson;

public class FastTests
{
    [Test]
    public void APointHoldsItsCoordinates()
    {
        var p = new Point(3, 4);
        Assert.Near(3, p.X);
        Assert.Near(4, p.Y);
    }

    [Test]
    public void LengthIsThePythagoreanDistance() =>
        Assert.Near(5, new Point(3, 4).Length());

    [Test]
    public void LengthOfTheOrigin() => Assert.Near(0, new Point(0, 0).Length());

    [Test]
    public void WithXProducesANewPoint()
    {
        var moved = new Point(1, 2).WithX(9);
        Assert.Near(9, moved.X);
        Assert.Near(2, moved.Y);
    }

    [Test]
    public void AssigningAStructCopiesIt()
    {
        // b is a full copy, not a reference - changing either cannot affect
        // the other, which is exactly what a value type means.
        var a = new Point(1, 2);
        var b = a;
        b = b.WithX(100);
        Assert.Near(1, a.X);
        Assert.Near(100, b.X);
    }

    [Test]
    public void TheDefaultStructIsZeroed()
    {
        Point p = default;
        Assert.Near(0, p.X);
        Assert.Near(0, p.Y);
    }

    [Test]
    public void SumDigitsIgnoresLetters() => Assert.Equal(3, Fast.SumDigits("a1b2c"));

    [Test]
    public void SumDigitsOfNoDigits() => Assert.Equal(0, Fast.SumDigits("abc"));

    [Test]
    public void SumDigitsOfAnEmptySpan() => Assert.Equal(0, Fast.SumDigits(""));

    [Test]
    public void SumDigitsWorksOnASlice()
    {
        // No substring is allocated - the span is a window onto the same chars.
        ReadOnlySpan<char> text = "xx12xx";
        Assert.Equal(3, Fast.SumDigits(text.Slice(2, 2)));
    }

    [Test]
    public void TryParseIntAcceptsANumber()
    {
        Assert.True(Fast.TryParseInt("1234", out int value));
        Assert.Equal(1234, value);
    }

    [Test]
    public void TryParseIntAcceptsANegative()
    {
        Assert.True(Fast.TryParseInt("-42", out int value));
        Assert.Equal(-42, value);
    }

    [Test]
    public void TryParseIntRejectsRubbish()
    {
        Assert.False(Fast.TryParseInt("12a", out int value));
        Assert.Equal(0, value);
        Assert.False(Fast.TryParseInt("", out _));
        Assert.False(Fast.TryParseInt("-", out _));
    }

    [Test]
    public void CountWordsCountsThem() => Assert.Equal(3, Fast.CountWords("one two three"));

    [Test]
    public void CountWordsIgnoresExtraSpaces() =>
        Assert.Equal(2, Fast.CountWords("  one   two  "));

    [Test]
    public void CountWordsOfAnEmptySpan() => Assert.Equal(0, Fast.CountWords(""));

    [Test]
    public void CountWordsOfOnlySpaces() => Assert.Equal(0, Fast.CountWords("   "));

    [Test]
    public void CountWordsOfOneWord() => Assert.Equal(1, Fast.CountWords("solo"));

    [Test]
    public void SumOfSquaresUsesTheScratchSpace() => Assert.Equal(14, Fast.SumOfSquares(3));

    [Test]
    public void SumOfSquaresOfZeroAndBelow()
    {
        Assert.Equal(0, Fast.SumOfSquares(0));
        Assert.Equal(0, Fast.SumOfSquares(-1));
    }

    [Test]
    public void SumOfSquaresBeyondTheStackallocThreshold() =>
        Assert.Equal(338350, Fast.SumOfSquares(100));
}
