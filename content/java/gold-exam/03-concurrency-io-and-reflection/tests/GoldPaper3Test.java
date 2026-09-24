import static org.junit.jupiter.api.Assertions.*;

import java.lang.annotation.RetentionPolicy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class GoldPaper3Test {

    @TempDir
    Path tmp;

    @Test
    void parallelSumOfASmallList() {
        assertEquals(6, GoldPaper3.parallelSum(List.of(1, 2, 3)));
    }

    @Test
    void parallelSumIsExactUnderLoad() {
        List<Integer> many = new ArrayList<>();
        for (int i = 0; i < 100000; i++) {
            many.add(1);
        }
        assertEquals(100000, GoldPaper3.parallelSum(many),
                "a shared int accumulator would lose increments here");
    }

    @Test
    void parallelSumOfEmpty() {
        assertEquals(0, GoldPaper3.parallelSum(List.of()));
    }

    @Test
    void countsWordsInAFile() throws Exception {
        Path p = tmp.resolve("a.txt");
        Files.writeString(p, "one two\nthree\n");
        assertEquals(3, GoldPaper3.wordCount(p));
    }

    @Test
    void ignoresBlankLinesAndExtraSpacing() throws Exception {
        Path p = tmp.resolve("b.txt");
        Files.writeString(p, "  one   two  \n\n\nthree\n");
        assertEquals(3, GoldPaper3.wordCount(p));
    }

    @Test
    void wordCountReleasesTheFile() throws Exception {
        Path p = tmp.resolve("c.txt");
        Files.writeString(p, "a b\n");
        GoldPaper3.wordCount(p);
        assertTrue(Files.deleteIfExists(p), "Files.lines must be closed");
    }

    @Test
    void theAnnotationSurvivesToRuntime() {
        java.lang.annotation.Retention r =
                GoldPaper3.Checked.class.getAnnotation(java.lang.annotation.Retention.class);
        assertNotNull(r, "the annotation needs a retention policy");
        assertEquals(RetentionPolicy.RUNTIME, r.value());
    }

    @Test
    void findsAnnotatedMethodsInOrder() {
        assertEquals(List.of("alpha", "beta"), GoldPaper3.annotatedNames(GoldPaper3.Sample.class));
    }

    @Test
    void skipsUnannotatedMethods() {
        assertFalse(GoldPaper3.annotatedNames(GoldPaper3.Sample.class).contains("gamma"));
    }

    @Test
    void safelyReturnsTheResult() {
        assertEquals(42, GoldPaper3.safely(() -> 42, -1));
    }

    @Test
    void safelyFallsBackOnAnyException() {
        assertEquals(-1, GoldPaper3.safely(() -> {
            throw new IllegalStateException("boom");
        }, -1));
        assertEquals(-1, GoldPaper3.safely(() -> {
            throw new java.io.IOException("checked too");
        }, -1));
    }
}
