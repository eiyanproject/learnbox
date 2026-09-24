import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class TextTest {

    @Test
    void shoutTrimsAndUppercases() {
        assertEquals("HELLO!", Text.shout("  hello "));
    }

    @Test
    void shoutOnAlreadyCleanInput() {
        assertEquals("JAVA!", Text.shout("java"));
    }

    @Test
    void reverseReversesTheCharacters() {
        assertEquals("avaj", Text.reverse("java"));
    }

    @Test
    void reverseOfEmptyIsEmpty() {
        assertEquals("", Text.reverse(""));
    }

    @Test
    void reverseOfOneCharacter() {
        assertEquals("x", Text.reverse("x"));
    }

    @Test
    void sameContentForEqualLiterals() {
        assertTrue(Text.sameContent("java", "java"));
    }

    @Test
    void sameContentForStringsBuiltAtRuntime() {
        // Built so it is NOT the pooled literal: == would be false here.
        String built = new StringBuilder("ja").append("va").toString();
        assertTrue(Text.sameContent("java", built),
                "compare content with equals, not identity with ==");
    }

    @Test
    void differentContentIsNotEqual() {
        assertFalse(Text.sameContent("java", "rust"));
    }

    @Test
    void initialsFromTwoNames() {
        assertEquals("A.L.", Text.initials("ada lovelace"));
    }

    @Test
    void initialsFromThreeNames() {
        assertEquals("A.L.K.", Text.initials("ada lovelace king"));
    }

    @Test
    void initialsIgnoreExtraSpacing() {
        assertEquals("G.H.", Text.initials("  grace   hopper "));
    }
}
