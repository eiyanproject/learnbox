import java.util.Map;
import java.util.Optional;

public class Maybe {

    public static Optional<String> find(Map<String, String> map, String key) {
        return Optional.ofNullable(map.get(key));
    }

    public static int nameLength(Map<String, String> map, String key) {
        return find(map, key).map(String::length).orElse(-1);
    }

    public static Optional<String> firstNonBlank(Optional<String> a, Optional<String> b) {
        return a.filter(s -> !s.isBlank()).or(() -> b.filter(s -> !s.isBlank()));
    }

    public static String requireValue(Optional<String> value) {
        return value.orElseThrow();
    }

    public static String orDefault(Optional<String> value, String fallback) {
        return value.orElse(fallback);
    }

    public static void main(String[] args) {
        System.out.println(nameLength(Map.of("a", "ada"), "a"));
    }
}
