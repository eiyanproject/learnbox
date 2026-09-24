import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class GoldPaper2 {

    public static double averageLength(List<String> items) {
        return items.stream().mapToInt(String::length).average().orElse(0);
    }

    public static Map<Character, List<String>> namesByInitial(List<String> items) {
        return items.stream().collect(Collectors.groupingBy(s -> s.charAt(0)));
    }

    public static long countLongerThan(List<String> items, int n) {
        return items.stream().filter(s -> s.length() > n).count();
    }

    public static String summarise(List<String> items) {
        if (items.isEmpty()) {
            return "none";
        }
        return items.get(0) + ".." + items.get(items.size() - 1) + " (" + items.size() + ")";
    }

    public static List<String> topN(List<String> items, int n) {
        return items.stream()
                .sorted(Comparator.comparingInt(String::length).reversed()
                        .thenComparing(Comparator.naturalOrder()))
                .limit(n)
                .collect(Collectors.toList());
    }

    public static void main(String[] args) {
        System.out.println(averageLength(List.of("ada", "grace")));
    }
}
