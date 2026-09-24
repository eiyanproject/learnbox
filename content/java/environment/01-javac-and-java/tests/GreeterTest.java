import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import org.junit.jupiter.api.Test;

class GreeterTest {

    @Test
    void greetsByName() {
        assertEquals("Hello, world!", Greeter.greet("world"));
    }

    @Test
    void greetsSomeoneElse() {
        assertEquals("Hello, Ada!", Greeter.greet("Ada"));
    }

    @Test
    void handlesAnEmptyName() {
        assertEquals("Hello, !", Greeter.greet(""));
    }

    @Test
    void greetIsStaticAndReturnsAString() throws Exception {
        Method m = Greeter.class.getMethod("greet", String.class);
        assertTrue(Modifier.isStatic(m.getModifiers()), "greet should be static");
        assertEquals(String.class, m.getReturnType(), "greet should return a String, not print");
    }

    @Test
    void mainHasTheRequiredSignature() throws Exception {
        Method m = Greeter.class.getMethod("main", String[].class);
        assertTrue(Modifier.isPublic(m.getModifiers()), "main must be public");
        assertTrue(Modifier.isStatic(m.getModifiers()), "main must be static");
        assertEquals(void.class, m.getReturnType(), "main must return void");
    }
}
