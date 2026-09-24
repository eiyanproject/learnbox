import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Files2 {

    public static void save(Path path, String text) {
        try {
            Path parent = path.getParent();
            if (parent != null) {
                Files.createDirectories(parent);
            }
            Files.writeString(path, text);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static String load(Path path, String fallback) {
        if (!Files.exists(path)) {
            return fallback;
        }
        try {
            return Files.readString(path);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static long countLines(Path path) {
        // Files.lines holds the file open: it must be closed.
        try (Stream<String> lines = Files.lines(path)) {
            return lines.count();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static void append(Path path, String line) {
        try {
            Files.writeString(path, line + System.lineSeparator(),
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static List<String> findContaining(Path path, String needle) {
        try (Stream<String> lines = Files.lines(path)) {
            return lines.filter(l -> l.contains(needle)).collect(Collectors.toList());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static void main(String[] args) throws IOException {
        Path p = Path.of("demo.txt");
        save(p, "one\ntwo\n");
        System.out.println(countLines(p));
        Files.deleteIfExists(p);
    }
}
