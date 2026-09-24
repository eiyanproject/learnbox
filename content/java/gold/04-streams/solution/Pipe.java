import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class Pipe {

    public static List<String> longNames(List<String> items, int n) {
        return items.stream()
                .filter(s -> s.length() > n)
                .map(String::toUpperCase)
                .collect(Collectors.toList());
    }

    public static int total(List<String> items) {
        return items.stream().mapToInt(String::length).sum();
    }

    public static Map<Integer, List<String>> groupByLength(List<String> items) {
        return items.stream().collect(Collectors.groupingBy(String::length));
    }

    public static Optional<String> firstMatching(List<String> items, Predicate<String> test) {
        return items.stream().filter(test).findFirst();
    }

    public static String joined(List<String> items) {
        return String.join(",", items);
    }

    public static void main(String[] args) {
        System.out.println(longNames(List.of("ada", "grace", "alan"), 3));
    }
}
