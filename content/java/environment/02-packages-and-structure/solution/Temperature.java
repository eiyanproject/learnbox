public class Temperature {

    public static final double ABSOLUTE_ZERO = -273.15;

    private double celsius;

    public Temperature(double celsius) {
        this.celsius = celsius;
    }

    public double getCelsius() {
        return celsius;
    }

    public void setCelsius(double celsius) {
        this.celsius = celsius;
    }

    public double toFahrenheit() {
        return celsius * 9.0 / 5.0 + 32;
    }

    public static void main(String[] args) {
        Temperature t = new Temperature(100);
        System.out.println(t.getCelsius() + "C is " + t.toFahrenheit() + "F");
    }
}
