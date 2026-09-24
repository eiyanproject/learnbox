public class Shapes {

    public static void main(String[] args) {
        Shape s = new Circle(2);
        System.out.println(s.describe());
        System.out.println(new Square(3).label());
    }
}

interface Named {
    String name();

    default String label() {
        return "<" + name() + ">";
    }
}

abstract class Shape implements Named {

    public abstract double area();

    public String describe() {
        return name() + " area=" + area();
    }
}

class Circle extends Shape implements Named {

    private final double radius;

    Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public String name() {
        return "circle";
    }

    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}

class Square extends Shape implements Named {

    private final double side;

    Square(double side) {
        this.side = side;
    }

    @Override
    public String name() {
        return "square";
    }

    @Override
    public double area() {
        return side * side;
    }
}
