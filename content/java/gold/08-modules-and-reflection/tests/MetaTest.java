import static org.junit.jupiter.api.Assertions.*;

import java.lang.annotation.RetentionPolicy;
import org.junit.jupiter.api.Test;

class MetaTest {

    @Test
    void theAnnotationIsRetainedAtRuntime() {
        java.lang.annotation.Retention r =
                Meta.Marked.class.getAnnotation(java.lang.annotation.Retention.class);
        assertNotNull(r, "Marked needs a @Retention policy");
        assertEquals(RetentionPolicy.RUNTIME, r.value(),
                "the default is CLASS, which reflection cannot see");
    }

    @Test
    void theAnnotationTargetsMethods() {
        assertNotNull(Meta.Marked.class.getAnnotation(java.lang.annotation.Target.class),
                "Marked should declare where it may be used");
    }

    @Test
    void findsTheAnnotatedMethods() {
        assertEquals(java.util.List.of("one", "two"), Meta.methodsWith(Meta.Sample.class));
    }

    @Test
    void doesNotIncludeUnannotatedMethods() {
        assertFalse(Meta.methodsWith(Meta.Sample.class).contains("three"));
    }

    @Test
    void resultIsSortedSoItIsDeterministic() {
        java.util.List<String> names = Meta.methodsWith(Meta.Sample.class);
        java.util.List<String> sorted = new java.util.ArrayList<>(names);
        java.util.Collections.sort(sorted);
        assertEquals(sorted, names, "getDeclaredMethods has no defined order");
    }

    @Test
    void readsTheAnnotationValue() {
        assertEquals("first", Meta.describeAnnotation(Meta.Sample.class, "one"));
    }

    @Test
    void reportsNoneForTheDefaultValue() {
        assertEquals("none", Meta.describeAnnotation(Meta.Sample.class, "two"));
    }

    @Test
    void reportsNoneForAnUnannotatedMethod() {
        assertEquals("none", Meta.describeAnnotation(Meta.Sample.class, "three"));
    }

    @Test
    void reportsNoneForAMethodThatDoesNotExist() {
        assertEquals("none", Meta.describeAnnotation(Meta.Sample.class, "nope"));
    }

    @Test
    void anEmptyClassHasNoAnnotatedMethods() {
        assertEquals(java.util.List.of(), Meta.methodsWith(String.class));
    }
}
