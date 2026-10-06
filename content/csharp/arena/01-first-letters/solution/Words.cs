namespace Lesson;

public static class Words
{
    public static string Acronym(string phrase) =>
        string.Concat(
            phrase.Split(new[] { ' ', '-' }, StringSplitOptions.RemoveEmptyEntries)
                .Where(piece => piece.Any(char.IsLetter))
                .Select(piece => char.ToUpperInvariant(piece.First(char.IsLetter))));

    public static bool IsIsogram(string word)
    {
        var letters = word.Where(char.IsLetter).Select(char.ToLowerInvariant).ToList();
        return letters.Distinct().Count() == letters.Count;
    }
}
