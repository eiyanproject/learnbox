import java.util.List;

public class Boxes {

    public static class Box<T> {

        private T value;

        public Box(T value) {
            this.value = value;
        }

        public T get() {
            return value;
        }

        public void set(T value) {
            this.value = value;
        }
    }

    public static double sumAll(List<? extends Number> values) {
        double total = 0;
        for (Number n : values) {
            total += n.doubleValue();
        }
        return total;
    }

    public static void addNumbers(List<? super Integer> target, int count) {
        for (int i = 1; i <= count; i++) {
            target.add(i);
        }
    }

    public static <T> T firstOrDefault(List<T> list, T fallback) {
        return list.isEmpty() ? fallback : list.get(0);
    }

    public static <T extends Comparable<T>> T largest(List<T> list) {
        if (list.isEmpty()) {
            throw new IllegalArgumentException("empty list has no largest element");
        }
        T best = list.get(0);
        for (T item : list) {
            if (item.compareTo(best) > 0) {
                best = item;
            }
        }
        return best;
    }

    public static void main(String[] args) {
        System.out.println(sumAll(List.of(1, 2.5)));
    }
}
