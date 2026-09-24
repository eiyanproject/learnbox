namespace Lesson;

public static class Calc
{
    public static int Add(int a, int b) => a + b;

    public static string Describe(int n) => n switch
    {
        < 0 => "negative",
        0 => "zero",
        _ => "positive",
    };

    public static double Average(int[] values)
    {
        if (values.Length == 0)
        {
            return 0;
        }
        // (double) on the sum, or the division happens in int and truncates.
        return (double)values.Sum() / values.Length;
    }

    public static string Repeat(string text, int count)
    {
        if (count < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(count), "count must not be negative");
        }
        return string.Concat(Enumerable.Repeat(text, count));
    }
}
