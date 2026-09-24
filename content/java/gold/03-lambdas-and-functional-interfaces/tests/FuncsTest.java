import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

class FuncsTest {

    @Test
    void transformWithALambda() {
        assertEquals("JAVA", Funcs.transform("java", s -> s.toUpperCase()));
    }

    @Test
    void transformWithAMethodReference() {
        assertEquals("JAVA", Funcs.transform("java", String::toUpperCase));
    }

    @Test
    void applyTwiceComposesTheFunction() {
        assertEquals(8, Funcs.applyTwice(n -> n * 2, 2));
        assertEquals(4, Funcs.applyTwice(n -> n + 1, 2));
    }

    @Test
    void describeAllMapsEveryItem() {
        assertEquals(List.of("A", "B"), Funcs.describeAll(List.of("a", "b"), String::toUpperCase));
    }

    @Test
    void describeAllLeavesTheInputAlone() {
        List<String> input = List.of("a");
        Funcs.describeAll(input, String::toUpperCase);
        assertEquals(List.of("a"), input);
    }

    @Test
    void describeAllOnAnEmptyList() {
        assertEquals(List.of(), Funcs.describeAll(List.of(), String::toUpperCase));
    }

    @Test
    void keepFiltersOnThePredicate() {
        assertEquals(List.of("aa", "bb"),
                Funcs.keep(List.of("aa", "c", "bb"), s -> s.length() == 2));
    }

    @Test
    void keepCanMatchNothing() {
        assertEquals(List.of(), Funcs.keep(List.of("a"), s -> s.isEmpty()));
    }

    @Test
    void counterCountsUp() {
        Supplier<Integer> c = Funcs.counter();
        assertEquals(1, c.get());
        assertEquals(2, c.get());
        assertEquals(3, c.get());
    }

    @Test
    void eachCounterIsIndependent() {
        Supplier<Integer> a = Funcs.counter();
        Supplier<Integer> b = Funcs.counter();
        a.get();
        a.get();
        assertEquals(1, b.get(), "a fresh counter starts again at 1");
    }

    @Test
    void transformerIsAFunctionalInterface() {
        assertNotNull(Funcs.Transformer.class.getAnnotation(FunctionalInterface.class),
                "mark it @FunctionalInterface so the compiler enforces the single method");
    }
}
