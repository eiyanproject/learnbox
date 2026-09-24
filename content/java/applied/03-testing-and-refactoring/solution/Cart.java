import java.util.LinkedHashMap;
import java.util.Map;

public class Cart {

    private record Line(int quantity, double unitPrice) {}

    private final Map<String, Line> lines = new LinkedHashMap<>();
    private double discount;

    public void addItem(String name, int quantity, double unitPrice) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("quantity must be positive");
        }
        lines.merge(name, new Line(quantity, unitPrice),
                (existing, added) -> new Line(existing.quantity() + added.quantity(),
                        existing.unitPrice()));
    }

    public int itemCount() {
        return lines.values().stream().mapToInt(Line::quantity).sum();
    }

    public double subtotal() {
        return lines.values().stream()
                .mapToDouble(l -> l.quantity() * l.unitPrice())
                .sum();
    }

    public void applyCoupon(String code) {
        discount = switch (code == null ? "" : code) {
            case "SAVE10" -> 0.10;
            case "HALF" -> 0.50;
            default -> throw new IllegalArgumentException("unknown coupon: " + code);
        };
    }

    public double total() {
        double value = subtotal() * (1 - discount);
        return Math.round(value * 100) / 100.0;
    }

    public static void main(String[] args) {
        Cart cart = new Cart();
        cart.addItem("apple", 2, 1.50);
        cart.applyCoupon("SAVE10");
        System.out.println(cart.total());
    }
}
