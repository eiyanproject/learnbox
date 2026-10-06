using Learnbox;
using Lesson;

public class TextBufferTests
{
    private static TextBuffer Typed(params string[] parts)
    {
        var buffer = new TextBuffer();
        foreach (var part in parts)
        {
            buffer.Append(part);
        }
        return buffer;
    }

    [Test]
    public void StartsEmpty()
    {
        var buffer = new TextBuffer();
        Assert.Equal("", buffer.Text);
        Assert.False(buffer.CanUndo);
        Assert.False(buffer.CanRedo);
        Assert.False(buffer.Undo());
        Assert.False(buffer.Redo());
        Assert.Equal("", buffer.Text);
    }

    [Test]
    public void Appending()
    {
        Assert.Equal("hello world", Typed("hello", " world").Text);
    }

    [Test]
    public void Deleting()
    {
        var buffer = Typed("hello world");
        buffer.Delete(3);
        Assert.Equal("hello wo", buffer.Text);
        buffer.Delete(100);
        Assert.Equal("", buffer.Text);
    }

    [Test]
    public void ANegativeCountIsRefused()
    {
        var buffer = Typed("abc");
        Assert.Throws<ArgumentOutOfRangeException>(() => buffer.Delete(-1));
        Assert.Equal("abc", buffer.Text);
    }

    [Test]
    public void UndoTakesBackOneEditAtATime()
    {
        var buffer = Typed("a", "b", "c");
        Assert.True(buffer.Undo());
        Assert.Equal("ab", buffer.Text);
        Assert.True(buffer.Undo());
        Assert.Equal("a", buffer.Text);
        Assert.True(buffer.Undo());
        Assert.Equal("", buffer.Text);
        Assert.False(buffer.Undo());
        Assert.Equal("", buffer.Text);
    }

    [Test]
    public void UndoBringsBackWhatWasDeleted()
    {
        var buffer = Typed("hello world");
        buffer.Delete(6);
        Assert.Equal("hello", buffer.Text);
        buffer.Undo();
        Assert.Equal("hello world", buffer.Text);
    }

    [Test]
    public void ADeleteLongerThanTheTextUndoesToTheWholeText()
    {
        var buffer = Typed("abc");
        buffer.Delete(50);
        buffer.Undo();
        Assert.Equal("abc", buffer.Text);
    }

    [Test]
    public void RedoPutsBackInOrder()
    {
        var buffer = Typed("a", "b", "c");
        buffer.Undo();
        buffer.Undo();
        Assert.True(buffer.Redo());
        Assert.Equal("ab", buffer.Text);
        Assert.True(buffer.Redo());
        Assert.Equal("abc", buffer.Text);
        Assert.False(buffer.Redo());
        Assert.Equal("abc", buffer.Text);
    }

    [Test]
    public void UndoAndRedoCanGoBackAndForth()
    {
        var buffer = Typed("x", "y");
        for (var i = 0; i < 5; i++)
        {
            buffer.Undo();
            Assert.Equal("x", buffer.Text);
            buffer.Redo();
            Assert.Equal("xy", buffer.Text);
        }
    }

    [Test]
    public void ANewEditThrowsAwayTheRedoHistory()
    {
        var buffer = Typed("a", "b", "c");
        buffer.Undo();
        buffer.Undo();
        buffer.Append("z");
        Assert.Equal("az", buffer.Text);
        Assert.False(buffer.CanRedo);
        Assert.False(buffer.Redo());
        Assert.Equal("az", buffer.Text);
        buffer.Undo();
        Assert.Equal("a", buffer.Text);
    }

    [Test]
    public void ADeleteIsANewEditToo()
    {
        var buffer = Typed("abc", "def");
        buffer.Undo();
        buffer.Delete(1);
        Assert.False(buffer.CanRedo);
        Assert.Equal("ab", buffer.Text);
    }

    [Test]
    public void EditsThatDoNothingAreNotEdits()
    {
        var buffer = Typed("a", "b");
        buffer.Undo();
        buffer.Append("");
        buffer.Delete(0);
        Assert.True(buffer.CanRedo);
        Assert.True(buffer.Redo());
        Assert.Equal("ab", buffer.Text);

        var empty = new TextBuffer();
        empty.Delete(3);
        empty.Append("");
        Assert.False(empty.CanUndo);
    }

    [Test]
    public void CanUndoAndCanRedoFollowTheHistory()
    {
        var buffer = Typed("a");
        Assert.True(buffer.CanUndo);
        Assert.False(buffer.CanRedo);
        buffer.Undo();
        Assert.False(buffer.CanUndo);
        Assert.True(buffer.CanRedo);
    }

    [Test]
    public void TheExample()
    {
        var buffer = Typed("hello", " world");
        buffer.Delete(3);
        Assert.Equal("hello wo", buffer.Text);
        buffer.Undo();
        Assert.Equal("hello world", buffer.Text);
        buffer.Undo();
        Assert.Equal("hello", buffer.Text);
        buffer.Redo();
        Assert.Equal("hello world", buffer.Text);
        buffer.Append("!");
        Assert.Equal("hello world!", buffer.Text);
        Assert.False(buffer.Redo());
    }

    [Test]
    public void TwoBuffersDoNotShare()
    {
        var a = Typed("a");
        var b = new TextBuffer();
        Assert.False(b.CanUndo);
        Assert.Equal("", b.Text);
        Assert.Equal("a", a.Text);
    }

    [Test]
    public void ALongSession()
    {
        var buffer = new TextBuffer();
        for (var i = 0; i < 500; i++)
        {
            buffer.Append("x");
        }
        for (var i = 0; i < 499; i++)
        {
            Assert.True(buffer.Undo());
        }
        Assert.Equal("x", buffer.Text);
        Assert.True(buffer.Undo());
        Assert.False(buffer.Undo());
    }
}
