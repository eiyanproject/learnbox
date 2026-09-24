import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import org.junit.jupiter.api.Test;

class ToolTest {

    private static final List<String> LINES =
            List.of("the cat sat", "on the mat", "and slept");

    @Test
    void parsesACommand() {
        assertEquals("count", Tool.parse(new String[] {"count"}).command());
    }

    @Test
    void parsesAFlagWithAValue() {
        Tool.Options o = Tool.parse(new String[] {"count", "--file", "a.txt"});
        assertEquals("a.txt", o.file());
    }

    @Test
    void parsesABooleanFlag() {
        assertTrue(Tool.parse(new String[] {"count", "--verbose"}).verbose());
        assertFalse(Tool.parse(new String[] {"count"}).verbose());
    }

    @Test
    void flagsCanComeInAnyOrder() {
        Tool.Options o = Tool.parse(new String[] {"--file", "a.txt", "find", "--pattern", "x"});
        assertEquals("find", o.command());
        assertEquals("a.txt", o.file());
        assertEquals("x", o.pattern());
    }

    @Test
    void anUnknownFlagIsRejectedByName() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class,
                () -> Tool.parse(new String[] {"count", "--fil", "a.txt"}));
        assertTrue(e.getMessage().contains("--fil"), "the message should name the bad flag");
    }

    @Test
    void aMissingCommandIsRejected() {
        assertThrows(IllegalArgumentException.class, () -> Tool.parse(new String[] {"--verbose"}));
    }

    @Test
    void aFlagWithoutItsValueIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> Tool.parse(new String[] {"count", "--file"}));
    }

    @Test
    void countCountsLines() {
        assertEquals("3", Tool.run(Tool.parse(new String[] {"count"}), LINES));
    }

    @Test
    void wordsCountsWords() {
        assertEquals("8", Tool.run(Tool.parse(new String[] {"words"}), LINES));
    }

    @Test
    void findReturnsMatchingLines() {
        String out = Tool.run(Tool.parse(new String[] {"find", "--pattern", "the"}), LINES);
        assertTrue(out.contains("the cat sat"));
        assertTrue(out.contains("on the mat"));
        assertFalse(out.contains("and slept"));
    }

    @Test
    void findWithoutAPatternIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> Tool.run(Tool.parse(new String[] {"find"}), LINES));
    }

    @Test
    void anUnknownCommandIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> Tool.run(Tool.parse(new String[] {"frobnicate"}), LINES));
    }

    @Test
    void runNeverTouchesTheDisk() {
        // The whole point of passing lines in: no file, no fixture, no I/O.
        assertEquals("0", Tool.run(Tool.parse(new String[] {"count"}), List.of()));
    }

    @Test
    void usageNamesTheCommands() {
        String usage = Tool.usage();
        assertTrue(usage.contains("count") && usage.contains("words") && usage.contains("find"));
    }
}
