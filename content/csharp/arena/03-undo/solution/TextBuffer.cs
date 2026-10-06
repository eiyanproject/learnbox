namespace Lesson;

public class TextBuffer
{
    // Whole snapshots: strings are immutable, so keeping the text as it was
    // before each edit is simpler than recording how to reverse it.
    private readonly Stack<string> _undo = new();
    private readonly Stack<string> _redo = new();

    public string Text { get; private set; } = "";

    private void Edit(string next)
    {
        _undo.Push(Text);
        _redo.Clear();
        Text = next;
    }

    public void Append(string text)
    {
        if (text.Length > 0)
        {
            Edit(Text + text);
        }
    }

    public void Delete(int count)
    {
        if (count < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(count));
        }
        if (count == 0 || Text.Length == 0)
        {
            return;
        }
        Edit(Text[..^Math.Min(count, Text.Length)]);
    }

    public bool Undo()
    {
        if (_undo.Count == 0)
        {
            return false;
        }
        _redo.Push(Text);
        Text = _undo.Pop();
        return true;
    }

    public bool Redo()
    {
        if (_redo.Count == 0)
        {
            return false;
        }
        _undo.Push(Text);
        Text = _redo.Pop();
        return true;
    }

    public bool CanUndo => _undo.Count > 0;

    public bool CanRedo => _redo.Count > 0;
}
