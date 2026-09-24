import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.Modifier;
import org.junit.jupiter.api.Test;

class ShapesTest {

    @Test
    void circleArea() {
        assertEquals(Math.PI * 4, new Circle(2).area(), 0.0001);
    }

    @Test
    void squareArea() {
        assertEquals(9.0, new Square(3).area(), 0.0001);
    }

    @Test
    void shapeIsAbstract() {
        assertTrue(Modifier.isAbstract(Shape.class.getModifiers()),
                "Shape should be abstract - there is no such thing as a plain shape");
    }

    @Test
    void namesComeFromTheSubclasses() {
        assertEquals("circle", new Circle(1).name());
        assertEquals("square", new Square(1).name());
    }

    @Test
    void theDefaultMethodIsInherited() {
        assertEquals("<circle>", new Circle(1).label());
        assertEquals("<square>", new Square(1).label());
    }

    @Test
    void describeDispatchesToTheSubclass() {
        // describe() lives on Shape and calls area(), which is overridden:
        // the object's runtime type decides which one runs.
        Shape s = new Square(3);
        assertEquals("square area=9.0", s.describe());
    }

    @Test
    void aShapeVariableCanHoldEitherSubclass() {
        Shape[] shapes = {new Circle(1), new Square(2)};
        assertEquals(Math.PI, shapes[0].area(), 0.0001);
        assertEquals(4.0, shapes[1].area(), 0.0001);
    }

    @Test
    void shapesAreAlsoNamed() {
        assertTrue(new Circle(1) instanceof Named, "a Circle should be usable as a Named");
    }

    @Test
    void patternMatchingInstanceofNarrowsTheType() {
        Shape s = new Circle(2);
        if (s instanceof Circle c) {
            assertEquals(Math.PI * 4, c.area(), 0.0001);
        } else {
            fail("the Circle should have matched");
        }
    }
}
