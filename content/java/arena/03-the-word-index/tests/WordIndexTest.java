import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;

class WordIndexTest {

    private static final List<String> LINES = List.of("The cat sat.", "The Cat? The mat!");

    @Test
    void theExample() {
        Map<String, List<Integer>> index = WordIndex.build(LINES);
        assertEquals(Map.of("cat", List.of(1, 2), "mat", List.of(2), "sat", List.of(1), "the", List.of(1, 2)), index);
    }

    @Test
    void keysComeOutInAlphabeticalOrder() {
        assertEquals(List.of("cat", "mat", "sat", "the"), new ArrayList<>(WordIndex.build(LINES).keySet()));
        assertEquals(List.of("apple", "mango", "zebra"),
                new ArrayList<>(WordIndex.build(List.of("zebra mango", "apple")).keySet()));
    }

    @Test
    void aWordTwiceOnOneLineIsListedOnce() {
        assertEquals(List.of(1), WordIndex.build(List.of("no no no")).get("no"));
        assertEquals(List.of(1, 3), WordIndex.build(List.of("go go", "stop", "go")).get("go"));
    }

    @Test
    void onlyLettersMakeWords() {
        Map<String, List<Integer>> index = WordIndex.build(List.of("don't stop-go 42 times, R2D2!"));
        assertEquals(List.of("d", "don", "go", "r", "stop", "t", "times"), new ArrayList<>(index.keySet()));
    }

    @Test
    void wordsAreLowerCased() {
        Map<String, List<Integer>> index = WordIndex.build(List.of("Java JAVA java"));
        assertEquals(Map.of("java", List.of(1)), index);
    }

    @Test
    void blankLinesStillCount() {
        Map<String, List<Integer>> index = WordIndex.build(List.of("one", "", "   ", "two"));
        assertEquals(List.of(1), index.get("one"));
        assertEquals(List.of(4), index.get("two"));
    }

    @Test
    void nothingIn() {
        assertTrue(WordIndex.build(List.of()).isEmpty());
        assertTrue(WordIndex.build(List.of("...", "123")).isEmpty());
        assertTrue(WordIndex.top(List.of(), 3).isEmpty());
    }

    @Test
    void topCountsEveryAppearance() {
        assertEquals(List.of("the", "cat"), WordIndex.top(LINES, 2));
        assertEquals(List.of("the"), WordIndex.top(LINES, 1));
    }

    @Test
    void levelWordsGoAlphabetically() {
        assertEquals(List.of("the", "cat", "mat", "sat"), WordIndex.top(LINES, 4));
        assertEquals(List.of("a", "b", "c"), WordIndex.top(List.of("c b a"), 3));
    }

    @Test
    void askingForMoreThanThereAre() {
        assertEquals(List.of("the", "cat", "mat", "sat"), WordIndex.top(LINES, 99));
    }

    @Test
    void askingForNone() {
        assertTrue(WordIndex.top(LINES, 0).isEmpty());
        assertTrue(WordIndex.top(LINES, -1).isEmpty());
    }

    @Test
    void aBiggerText() {
        List<String> lines = new ArrayList<>();
        for (int i = 0; i < 300; i++) {
            lines.add("alpha beta" + (i % 2 == 0 ? " gamma" : "") + (i % 3 == 0 ? " beta" : ""));
        }
        assertEquals(List.of("beta", "alpha", "gamma"), WordIndex.top(lines, 3));
        Map<String, List<Integer>> index = WordIndex.build(lines);
        assertEquals(300, index.get("alpha").size());
        assertEquals(150, index.get("gamma").size());
        assertEquals(List.of(1, 3, 5), index.get("gamma").subList(0, 3));
    }
}
