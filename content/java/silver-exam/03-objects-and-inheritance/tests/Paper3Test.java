import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class Paper3Test {

    @Test
    void baseAnimalSpeaks() {
        assertEquals("...", new Animal("x").speak());
    }

    @Test
    void noArgumentConstructorChains() {
        assertEquals("unnamed", new Animal().getName(),
                "the no-argument constructor should call this(\"unnamed\")");
    }

    @Test
    void subclassesOverrideSpeak() {
        assertEquals("woof", new Dog("rex").speak());
        assertEquals("meow", new Cat("tom").speak());
    }

    @Test
    void subclassConstructorPassesTheNameUp() {
        assertEquals("rex", new Dog("rex").getName());
    }

    @Test
    void describeUsesTheOverriddenMethod() {
        // describe() is defined on Animal and calls speak(); the Dog's version
        // runs because dispatch follows the object, not the declaring class.
        assertEquals("rex says woof", new Dog("rex").describe());
    }

    @Test
    void aParentVariableRunsTheChildImplementation() {
        Animal a = new Dog("rex");
        assertEquals("woof", a.speak());
    }

    @Test
    void soundOfAcceptsAnySubclass() {
        assertEquals("woof", Paper3.soundOf(new Dog("rex")));
        assertEquals("meow", Paper3.soundOf(new Cat("tom")));
        assertEquals("...", Paper3.soundOf(new Animal("generic")));
    }

    @Test
    void subclassesAreAnimals() {
        assertTrue(new Dog("rex") instanceof Animal);
        assertTrue(new Cat("tom") instanceof Animal);
    }

    @Test
    void polymorphicArray() {
        Animal[] zoo = {new Dog("a"), new Cat("b"), new Animal("c")};
        assertEquals("woof", zoo[0].speak());
        assertEquals("meow", zoo[1].speak());
        assertEquals("...", zoo[2].speak());
    }
}
