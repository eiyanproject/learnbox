import java.io.IOException;
import java.io.UncheckedIOException;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.stream.Stream;

public class GoldPaper3 {

    public static long parallelSum(List<Integer> values) {
        // No shared mutable state, so parallelism is safe by construction.
        return values.parallelStream().mapToLong(Integer::longValue).sum();
    }

    public static long wordCount(Path path) {
        try (Stream<String> lines = Files.lines(path)) {
            return lines.flatMap(l -> Stream.of(l.trim().split("\\s+")))
                    .filter(w -> !w.isEmpty())
                    .count();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface Checked {
    }

    public static class Sample {

        @Checked
        public void alpha() {}

        @Checked
        public void beta() {}

        public void gamma() {}
    }

    public static List<String> annotatedNames(Class<?> type) {
        List<String> names = new ArrayList<>();
        for (Method m : type.getDeclaredMethods()) {
            if (m.isAnnotationPresent(Checked.class)) {
                names.add(m.getName());
            }
        }
        Collections.sort(names);
        return names;
    }

    public static <T> T safely(Callable<T> task, T fallback) {
        try {
            return task.call();
        } catch (Exception e) {
            return fallback;
        }
    }

    public static void main(String[] args) {
        System.out.println(parallelSum(List.of(1, 2, 3)));
    }
}
