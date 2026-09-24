import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;

public class Store {

    public static Map<String, Integer> countWords(String text) {
        Map<String, Integer> counts = new LinkedHashMap<>();
        for (String word : text.toLowerCase().split("\\s+")) {
            if (!word.isEmpty()) {
                counts.merge(word, 1, Integer::sum);
            }
        }
        return counts;
    }

    public static String firstUnique(String text) {
        for (Map.Entry<String, Integer> e : countWords(text).entrySet()) {
            if (e.getValue() == 1) {
                return e.getKey();
            }
        }
        return null;
    }

    public static List<Map.Entry<String, Integer>> sortedByValue(Map<String, Integer> counts) {
        List<Map.Entry<String, Integer>> entries = new ArrayList<>(counts.entrySet());
        entries.sort(Map.Entry.<String, Integer>comparingByValue()
                .reversed()
                .thenComparing(Map.Entry.comparingByKey()));
        return entries;
    }

    public static List<String> dedupe(List<String> items) {
        return new ArrayList<>(new LinkedHashSet<>(items));
    }

    public static void main(String[] args) {
        System.out.println(countWords("the cat the dog"));
    }
}
