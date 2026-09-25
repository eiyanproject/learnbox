namespace Lesson;

// readonly on the struct makes every field readonly and lets the compiler skip
// the defensive copies it would otherwise make on every member access.
public readonly struct Point
{
    public Point(double x, double y)
    {
        X = x;
        Y = y;
    }

    public double X { get; }

    public double Y { get; }

    public double Length() => Math.Sqrt(X * X + Y * Y);

    /// <summary>A new Point - a readonly struct cannot be changed in place.</summary>
    public Point WithX(double x) => new Point(x, Y);
}

public static class Fast
{
    public static int SumDigits(ReadOnlySpan<char> text)
    {
        int total = 0;
        for (int i = 0; i < text.Length; i++)
        {
            if (char.IsAsciiDigit(text[i]))
            {
                total += text[i] - '0';
            }
        }
        return total;
    }

    public static bool TryParseInt(ReadOnlySpan<char> text, out int value)
    {
        value = 0;
        if (text.Length == 0)
        {
            return false;
        }
        int start = 0;
        bool negative = false;
        if (text[0] == '-')
        {
            negative = true;
            start = 1;
            if (text.Length == 1)
            {
                return false;
            }
        }
        long result = 0;
        for (int i = start; i < text.Length; i++)
        {
            if (!char.IsAsciiDigit(text[i]))
            {
                value = 0;
                return false;
            }
            result = result * 10 + (text[i] - '0');
        }
        value = (int)(negative ? -result : result);
        return true;
    }

    public static int CountWords(ReadOnlySpan<char> text)
    {
        // Slicing is a window onto the same memory; Substring would allocate a
        // new string per word.
        int words = 0;
        while (text.Length > 0)
        {
            int space = text.IndexOf(' ');
            ReadOnlySpan<char> word = space < 0 ? text : text.Slice(0, space);
            if (word.Length > 0)
            {
                words++;
            }
            text = space < 0 ? ReadOnlySpan<char>.Empty : text.Slice(space + 1);
        }
        return words;
    }

    public static int SumOfSquares(int n)
    {
        if (n <= 0)
        {
            return 0;
        }
        // Scratch space on the stack: no allocation, nothing for the GC.
        Span<int> scratch = n <= 64 ? stackalloc int[n] : new int[n];
        for (int i = 0; i < n; i++)
        {
            scratch[i] = (i + 1) * (i + 1);
        }
        int total = 0;
        foreach (int value in scratch)
        {
            total += value;
        }
        return total;
    }
}
