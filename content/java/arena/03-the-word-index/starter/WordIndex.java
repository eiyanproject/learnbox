import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class WordIndex {

    public static Map<String, List<Integer>> build(List<String> lines) {
        return new TreeMap<>();
    }

    public static List<String> top(List<String> lines, int n) {
        return new ArrayList<>();
    }

    public static void main(String[] args) {
        System.out.println(build(List.of("The cat sat.", "The Cat? The mat!")));
    }
}
