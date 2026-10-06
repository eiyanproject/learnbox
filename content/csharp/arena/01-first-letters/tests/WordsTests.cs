using Learnbox;
using Lesson;

public class WordsTests
{
    [Test]
    public void AcronymOfPlainWords() =>
        Assert.Equal("PNG", Words.Acronym("portable network graphics"));

    [Test]
    public void AcronymKeepsCapitalsAndRaisesTheRest() =>
        Assert.Equal("HTML", Words.Acronym("hyper Text markup Language"));

    [Test]
    public void HyphensSeparateWords() =>
        Assert.Equal("CMOS", Words.Acronym("Complementary metal-oxide semiconductor"));

    [Test]
    public void ExtraSpacesAreNotWords() =>
        Assert.Equal("ASAP", Words.Acronym("  as   soon as possible "));

    [Test]
    public void PunctuationIsSkippedOver()
    {
        Assert.Equal("TQF", Words.Acronym("the 'quick' fox"));
        Assert.Equal("RSVP", Words.Acronym("(repondez) s'il vous plait"));
    }

    [Test]
    public void APieceWithNoLettersAddsNothing()
    {
        Assert.Equal("GT", Words.Acronym("gate 42 - terminal"));
        Assert.Equal("", Words.Acronym("12 - 34"));
    }

    [Test]
    public void AcronymOfNothing()
    {
        Assert.Equal("", Words.Acronym(""));
        Assert.Equal("", Words.Acronym("   "));
    }

    [Test]
    public void Isograms()
    {
        Assert.True(Words.IsIsogram("lumberjacks"));
        Assert.True(Words.IsIsogram("background"));
    }

    [Test]
    public void NotIsograms()
    {
        Assert.False(Words.IsIsogram("letter"));
        Assert.False(Words.IsIsogram("isograms"));
    }

    [Test]
    public void CaseDoesNotHideARepeat()
    {
        Assert.False(Words.IsIsogram("Alpha"));
        Assert.False(Words.IsIsogram("moOse"));
    }

    [Test]
    public void OnlyLettersCount()
    {
        Assert.True(Words.IsIsogram("six-year-old"));
        Assert.True(Words.IsIsogram("big duck 22"));
        Assert.False(Words.IsIsogram("big dog"));
    }

    [Test]
    public void NothingRepeatsInNothing()
    {
        Assert.True(Words.IsIsogram(""));
        Assert.True(Words.IsIsogram("- -"));
    }
}
