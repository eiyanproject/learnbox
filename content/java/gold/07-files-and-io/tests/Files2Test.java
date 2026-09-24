import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class Files2Test {

    @TempDir
    Path tmp;

    @Test
    void saveThenLoad() {
        Path p = tmp.resolve("a.txt");
        Files2.save(p, "hello");
        assertEquals("hello", Files2.load(p, "missing"));
    }

    @Test
    void saveCreatesParentDirectories() {
        Path p = tmp.resolve("deep/nested/a.txt");
        Files2.save(p, "hi");
        assertTrue(Files.exists(p), "the parent directories should have been created");
    }

    @Test
    void saveTruncatesAnExistingFile() {
        Path p = tmp.resolve("a.txt");
        Files2.save(p, "a long piece of text");
        Files2.save(p, "short");
        assertEquals("short", Files2.load(p, ""));
    }

    @Test
    void loadFallsBackWhenMissing() {
        assertEquals("missing", Files2.load(tmp.resolve("nope.txt"), "missing"));
    }

    @Test
    void countsLines() {
        Path p = tmp.resolve("lines.txt");
        Files2.save(p, "one\ntwo\nthree\n");
        assertEquals(3, Files2.countLines(p));
    }

    @Test
    void countsZeroLinesInAnEmptyFile() throws IOException {
        Path p = tmp.resolve("empty.txt");
        Files.writeString(p, "");
        assertEquals(0, Files2.countLines(p));
    }

    @Test
    void countLinesReleasesTheFile() throws IOException {
        // If the stream were left open, deleting would fail on some platforms
        // and the handle would leak on all of them.
        Path p = tmp.resolve("lines.txt");
        Files2.save(p, "a\nb\n");
        Files2.countLines(p);
        assertTrue(Files.deleteIfExists(p), "the file should no longer be held open");
    }

    @Test
    void appendAddsToTheEnd() {
        Path p = tmp.resolve("log.txt");
        Files2.append(p, "first");
        Files2.append(p, "second");
        assertEquals(2, Files2.countLines(p));
        assertTrue(Files2.load(p, "").startsWith("first"));
    }

    @Test
    void appendCreatesTheFileIfMissing() {
        Path p = tmp.resolve("new.txt");
        Files2.append(p, "line");
        assertTrue(Files.exists(p));
    }

    @Test
    void findContainingFiltersLines() {
        Path p = tmp.resolve("log.txt");
        Files2.save(p, "error one\nok\nerror two\n");
        assertEquals(List.of("error one", "error two"), Files2.findContaining(p, "error"));
    }

    @Test
    void findContainingCanMatchNothing() {
        Path p = tmp.resolve("log.txt");
        Files2.save(p, "ok\n");
        assertEquals(List.of(), Files2.findContaining(p, "error"));
    }
}
