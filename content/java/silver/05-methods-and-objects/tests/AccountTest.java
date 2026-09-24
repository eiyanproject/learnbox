import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class AccountTest {

    @Test
    void twoArgumentConstructor() {
        Account a = new Account("ada", 50);
        assertEquals("ada", a.getOwner());
        assertEquals(50.0, a.getBalance(), 0.0001);
    }

    @Test
    void oneArgumentConstructorStartsAtZero() {
        assertEquals(0.0, new Account("bob").getBalance(), 0.0001);
    }

    @Test
    void depositAddsToTheBalance() {
        Account a = new Account("ada");
        a.deposit(30);
        a.deposit(20);
        assertEquals(50.0, a.getBalance(), 0.0001);
    }

    @Test
    void depositRejectsZeroAndNegative() {
        Account a = new Account("ada");
        assertThrows(IllegalArgumentException.class, () -> a.deposit(0));
        assertThrows(IllegalArgumentException.class, () -> a.deposit(-5));
    }

    @Test
    void withdrawSubtracts() {
        Account a = new Account("ada", 100);
        a.withdraw(40);
        assertEquals(60.0, a.getBalance(), 0.0001);
    }

    @Test
    void withdrawRejectsMoreThanTheBalance() {
        Account a = new Account("ada", 10);
        assertThrows(IllegalArgumentException.class, () -> a.withdraw(11));
        assertEquals(10.0, a.getBalance(), 0.0001, "a rejected withdrawal must not change the balance");
    }

    @Test
    void transferMovesMoneyBothWays() {
        Account a = new Account("ada", 100);
        Account b = new Account("bob");
        a.transferTo(b, 25);
        assertEquals(75.0, a.getBalance(), 0.0001);
        assertEquals(25.0, b.getBalance(), 0.0001);
    }

    @Test
    void aFailedTransferLeavesBothUnchanged() {
        Account a = new Account("ada", 10);
        Account b = new Account("bob", 5);
        assertThrows(IllegalArgumentException.class, () -> a.transferTo(b, 50));
        assertEquals(10.0, a.getBalance(), 0.0001);
        assertEquals(5.0, b.getBalance(), 0.0001,
                "withdraw should fail before anything is deposited");
    }

    @Test
    void mutatingThroughAParameterIsVisibleToTheCaller() {
        // Pass by value of the reference: the object is shared.
        Account a = new Account("ada", 100);
        Account b = new Account("bob");
        a.transferTo(b, 10);
        assertEquals(10.0, b.getBalance(), 0.0001);
    }
}
