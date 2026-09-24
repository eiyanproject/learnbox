import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.function.UnaryOperator;

public class Funcs {

    @FunctionalInterface
    public interface Transformer {
        String apply(String input);
    }

    public static String transform(String s, Transformer t) {
        return t.apply(s);
    }

    public static int applyTwice(UnaryOperator<Integer> f, int x) {
        return f.apply(f.apply(x));
    }

    public static List<String> describeAll(List<String> items, Function<String, String> f) {
        List<String> out = new ArrayList<>();
        for (String item : items) {
            out.add(f.apply(item));
        }
        return out;
    }

    public static List<String> keep(List<String> items, Predicate<String> test) {
        List<String> out = new ArrayList<>();
        for (String item : items) {
            if (test.test(item)) {
                out.add(item);
            }
        }
        return out;
    }

    public static Supplier<Integer> counter() {
        // A captured local must be effectively final, so the mutable state
        // lives inside an array the lambda closes over.
        int[] n = {0};
        return () -> ++n[0];
    }

    public static void main(String[] args) {
        System.out.println(transform("java", String::toUpperCase));
    }
}
