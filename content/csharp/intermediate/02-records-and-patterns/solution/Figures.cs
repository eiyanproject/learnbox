namespace Lesson;

public abstract record Shape;

public record Circle(double Radius) : Shape;

public record Rect(double Width, double Height) : Shape;

public static class Figures
{
    public static double Area(Shape s) => s switch
    {
        Circle c => Math.PI * c.Radius * c.Radius,
        Rect r => r.Width * r.Height,
        _ => throw new ArgumentException($"unknown shape: {s.GetType().Name}"),
    };

    // The first match wins, so the square case has to come before the general
    // rectangle one.
    public static string Classify(Shape s) => s switch
    {
        Circle => "circle",
        Rect { Width: var w, Height: var h } when w == h => "square",
        Rect => "rectangle",
        _ => "unknown",
    };

    public static string Band(int n) => n switch
    {
        < 0 => "negative",
        0 => "zero",
        > 0 and < 10 => "small",
        _ => "large",
    };

    // `with` copies and replaces; r itself is untouched.
    public static Rect Grow(Rect r, double factor) =>
        r with { Width = r.Width * factor, Height = r.Height * factor };
}
