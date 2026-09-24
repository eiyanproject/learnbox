import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Meta {

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface Marked {
        String value() default "";
    }

    public static class Sample {

        @Marked("first")
        public void one() {}

        @Marked
        public void two() {}

        public void three() {}
    }

    public static List<String> methodsWith(Class<?> type) {
        List<String> names = new ArrayList<>();
        for (Method m : type.getDeclaredMethods()) {
            if (m.isAnnotationPresent(Marked.class)) {
                names.add(m.getName());
            }
        }
        // Reflection does not promise an order, so impose one.
        Collections.sort(names);
        return names;
    }

    public static String describeAnnotation(Class<?> type, String methodName) {
        for (Method m : type.getDeclaredMethods()) {
            if (m.getName().equals(methodName) && m.isAnnotationPresent(Marked.class)) {
                String value = m.getAnnotation(Marked.class).value();
                return value.isEmpty() ? "none" : value;
            }
        }
        return "none";
    }

    public static void main(String[] args) {
        System.out.println(methodsWith(Sample.class));
    }
}
