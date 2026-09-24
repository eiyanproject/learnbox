import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class Paper1Test {

    @Test
    void integerDivisionTruncates() {
        assertEquals(3, Paper1.evaluate(7, 2));
    }

    @Test
    void divisionTowardsZeroForNegatives() {
        assertEquals(-3, Paper1.evaluate(-7, 2), "Java truncates towards zero, so -3 not -4");
    }

    @ParameterizedTest
    @CsvSource({
        "byte,byte,int", "short,short,int", "int,int,int", "byte,int,int",
        "int,long,long", "long,long,long", "long,float,float",
        "int,double,double", "float,double,double"
    })
    void promotionRules(String left, String right, String expected) {
        assertEquals(expected, Paper1.promote(left, right));
    }

    @ParameterizedTest
    @CsvSource({"-5,negative", "0,zero", "7,positive"})
    void ternaryChain(int n, String expected) {
        assertEquals(expected, Paper1.ternaryChain(n));
    }

    @ParameterizedTest
    @CsvSource({"15,FizzBuzz", "30,FizzBuzz", "3,Fizz", "9,Fizz", "5,Buzz", "10,Buzz", "7,7", "1,1"})
    void fizzOrBuzz(int n, String expected) {
        assertEquals(expected, Paper1.fizzOrBuzz(n));
    }

    @Test
    void compoundAssignmentWraps() {
        // b += 300 compiles because += casts implicitly; b = b + 300 does not.
        assertEquals((byte) (10 + 300), Paper1.compound((byte) 10, 300));
    }

    @Test
    void compoundAssignmentWithinRange() {
        assertEquals((byte) 30, Paper1.compound((byte) 10, 20));
    }
}
