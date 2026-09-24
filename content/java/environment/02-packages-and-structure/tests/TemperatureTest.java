import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import org.junit.jupiter.api.Test;

class TemperatureTest {

    @Test
    void constructorAndGetter() {
        assertEquals(20.0, new Temperature(20).getCelsius(), 0.0001);
    }

    @Test
    void setterChangesTheValue() {
        Temperature t = new Temperature(0);
        t.setCelsius(37.5);
        assertEquals(37.5, t.getCelsius(), 0.0001);
    }

    @Test
    void convertsFreezingPoint() {
        assertEquals(32.0, new Temperature(0).toFahrenheit(), 0.0001);
    }

    @Test
    void convertsBoilingPoint() {
        assertEquals(212.0, new Temperature(100).toFahrenheit(), 0.0001);
    }

    @Test
    void doesNotTruncateWithIntegerDivision() {
        // 37 * 9 / 5 + 32 is 98.6, but with int division it comes out 98.0.
        assertEquals(98.6, new Temperature(37).toFahrenheit(), 0.0001);
    }

    @Test
    void theFieldIsPrivate() throws Exception {
        Field f = Temperature.class.getDeclaredField("celsius");
        assertTrue(Modifier.isPrivate(f.getModifiers()),
                "celsius should be private - that is what encapsulation means here");
    }

    @Test
    void absoluteZeroIsAPublicStaticFinalConstant() throws Exception {
        Field f = Temperature.class.getField("ABSOLUTE_ZERO");
        int mods = f.getModifiers();
        assertTrue(Modifier.isPublic(mods), "ABSOLUTE_ZERO should be public");
        assertTrue(Modifier.isStatic(mods), "ABSOLUTE_ZERO should be static");
        assertTrue(Modifier.isFinal(mods), "ABSOLUTE_ZERO should be final");
        assertEquals(-273.15, (double) f.get(null), 0.0001);
    }
}
