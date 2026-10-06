import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class WordIndex {

    private static List<String> words(String line) {
        List<String> out = new ArrayList<>();
        for (String piece : line.toLowerCase().split("[^\\p{L}]+")) {
            if (!piece.isEmpty()) {
                out.add(piece);
            }
        }
        return out;
    }

    public static Map<String, List<Integer>> build(List<String> lines) {
        Map<String, List<Integer>> index = new TreeMap<>();
        for (int i = 0; i < lines.size(); i++) {
            int number = i + 1;
            for (String word : words(lines.get(i))) {
                List<Integer> where = index.computeIfAbsent(word, k -> new ArrayList<>());
                if (where.isEmpty() || where.get(where.size() - 1) != number) {
                    where.add(number);
                }
            }
        }
        return index;
    }

    public static List<String> top(List<String> lines, int n) {
        Map<String, Integer> counts = new HashMap<>();
        for (String line : lines) {
            for (String word : words(line)) {
                counts.merge(word, 1, Integer::sum);
            }
        }
        List<String> ranked = new ArrayList<>(counts.keySet());
        ranked.sort(Comparator.comparing((String w) -> -counts.get(w)).thenComparing(Comparator.naturalOrder()));
        return new ArrayList<>(ranked.subList(0, Math.max(0, Math.min(n, ranked.size()))));
    }

    public static void main(String[] args) {
        System.out.println(build(List.of("The cat sat.", "The Cat? The mat!")));
    }
}
