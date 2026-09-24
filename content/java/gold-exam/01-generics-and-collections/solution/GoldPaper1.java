import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class GoldPaper1 {

    public static <T> void copy(List<? extends T> src, List<? super T> dst) {
        for (T item : src) {
            dst.add(item);
        }
    }

    public static class Pair<A, B> {

        private final A first;
        private final B second;

        public Pair(A first, B second) {
            this.first = first;
            this.second = second;
        }

        public A getFirst() {
            return first;
        }

        public B getSecond() {
            return second;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) {
                return true;
            }
            if (!(o instanceof Pair)) {
                return false;
            }
            Pair<?, ?> other = (Pair<?, ?>) o;
            return Objects.equals(first, other.first) && Objects.equals(second, other.second);
        }

        @Override
        public int hashCode() {
            return Objects.hash(first, second);
        }
    }

    public static <T> Map<T, Integer> frequency(List<T> items) {
        Map<T, Integer> counts = new LinkedHashMap<>();
        for (T item : items) {
            counts.merge(item, 1, Integer::sum);
        }
        return counts;
    }

    public static <T> List<T> intersection(List<T> a, List<T> b) {
        LinkedHashSet<T> out = new LinkedHashSet<>();
        for (T item : a) {
            if (b.contains(item)) {
                out.add(item);
            }
        }
        return new ArrayList<>(out);
    }

    public static void main(String[] args) {
        System.out.println(frequency(List.of("a", "b", "a")));
    }
}
