import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

public class Core {

    public static boolean boxedEquals(Integer a, Integer b) {
        return a.equals(b);
    }

    public static int safeUnbox(Integer value, int fallback) {
        return value == null ? fallback : value;
    }

    public static long daysBetween(LocalDate a, LocalDate b) {
        return ChronoUnit.DAYS.between(a, b);
    }

    public static LocalDate addWeeks(LocalDate date, int weeks) {
        return date.plusWeeks(weeks);
    }

    public record Point(int x, int y) {
        public double distanceFromOrigin() {
            return Math.sqrt(x * x + y * y);
        }
    }

    public static void main(String[] args) {
        System.out.println(new Point(3, 4).distanceFromOrigin());
    }
}
