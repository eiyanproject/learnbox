public class Paper3 {

    public static String soundOf(Animal a) {
        return a.speak();
    }

    public static void main(String[] args) {
        Animal a = new Dog("rex");
        System.out.println(a.describe());
    }
}

class Animal {

    private final String name;

    Animal(String name) {
        this.name = name;
    }

    Animal() {
        this("unnamed");
    }

    public String getName() {
        return name;
    }

    public String speak() {
        return "...";
    }

    public String describe() {
        return getName() + " says " + speak();
    }
}

class Dog extends Animal {

    Dog(String name) {
        super(name);
    }

    @Override
    public String speak() {
        return "woof";
    }
}

class Cat extends Animal {

    Cat(String name) {
        super(name);
    }

    @Override
    public String speak() {
        return "meow";
    }
}
