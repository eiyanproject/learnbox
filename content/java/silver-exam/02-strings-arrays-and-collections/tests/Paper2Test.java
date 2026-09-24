import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class Paper2Test {

    @Test
    void chainedAppliesEveryStep() {
        assertEquals("HELLO_WORLD", Paper2.chained("  hello world "));
    }

    @Test
    void chainedOnAlreadyCleanInput() {
        assertEquals("JAVA", Paper2.chained("java"));
    }

    @Test
    void identicalIsTrueForThePooledLiteral() {
        assertTrue(Paper2.identical("java", "java"), "literals are interned, so they are one object");
    }

    @Test
    void identicalIsFalseForARuntimeString() {
        String built = new StringBuilder("ja").append("va").toString();
        assertFalse(Paper2.identical("java", built), "identical should be ==, which is false here");
    }

    @Test
    void equivalentIsTrueForBoth() {
        String built = new StringBuilder("ja").append("va").toString();
        assertTrue(Paper2.equivalent("java", "java"));
        assertTrue(Paper2.equivalent("java", built), "equivalent should be equals, which compares content");
    }

    @Test
    void sameElementsComparesContents() {
        assertTrue(Paper2.sameElements(new int[] {1, 2}, new int[] {1, 2}),
                "two distinct arrays with the same contents - equals() would say false");
    }

    @Test
    void sameElementsIsFalseWhenTheyDiffer() {
        assertFalse(Paper2.sameElements(new int[] {1, 2}, new int[] {2, 1}));
        assertFalse(Paper2.sameElements(new int[] {1}, new int[] {1, 2}));
    }

    @Test
    void describeShowsContentsNotAHash() {
        String out = Paper2.describe(new int[] {1, 2, 3});
        assertEquals("[1, 2, 3] len=3", out);
        assertFalse(out.contains("[I@"), "use Arrays.toString rather than the array itself");
    }

    @Test
    void describeAnEmptyArray() {
        assertEquals("[] len=0", Paper2.describe(new int[] {}));
    }

    @Test
    void middleThird() {
        assertEquals("mid", Paper2.middle("premidpost".substring(0, 9)));
        assertEquals("b", Paper2.middle("abc"));
    }

    @Test
    void middleUsesAnExclusiveEnd() {
        assertEquals("34", Paper2.middle("123456"), "substring(2, 4) is two characters, not three");
    }
}
