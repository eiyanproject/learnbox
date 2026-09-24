import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class BookingTest {

    @Test
    void newBookingsStartPending() {
        assertEquals(Status.PENDING, Reservation.of("AB123", 2).status());
    }

    @Test
    void accessorsComeFromTheRecord() {
        Reservation r = Reservation.of("AB123", 2);
        assertEquals("AB123", r.reference());
        assertEquals(2, r.guests());
    }

    @Test
    void confirmProducesANewConfirmedBooking() {
        Reservation pending = Reservation.of("AB123", 2);
        Reservation confirmed = pending.confirm();
        assertEquals(Status.CONFIRMED, confirmed.status());
        assertEquals(Status.PENDING, pending.status(), "a record is immutable");
    }

    @Test
    void cancelProducesACancelledBooking() {
        assertEquals(Status.CANCELLED, Reservation.of("AB123", 2).cancel().status());
    }

    @Test
    void confirmKeepsTheOtherFields() {
        Reservation c = Reservation.of("AB123", 4).confirm();
        assertEquals("AB123", c.reference());
        assertEquals(4, c.guests());
    }

    @Test
    void onlyCancelledIsFinal() {
        assertTrue(Status.CANCELLED.isFinal());
        assertFalse(Status.PENDING.isFinal());
        assertFalse(Status.CONFIRMED.isFinal());
    }

    @Test
    void guestsMustBeAtLeastOne() {
        assertThrows(IllegalArgumentException.class, () -> Reservation.of("AB123", 0));
        assertThrows(IllegalArgumentException.class, () -> Reservation.of("AB123", -1));
    }

    @Test
    void referenceMustNotBeBlankOrNull() {
        assertThrows(IllegalArgumentException.class, () -> Reservation.of("", 1));
        assertThrows(IllegalArgumentException.class, () -> Reservation.of("   ", 1));
        assertThrows(IllegalArgumentException.class, () -> Reservation.of(null, 1));
    }

    @Test
    void validationRunsForEveryConstructionPath() {
        // The compact constructor guards the canonical constructor too.
        assertThrows(IllegalArgumentException.class,
                () -> new Reservation("AB1", 0, Status.CONFIRMED));
    }

    @Test
    void equalBookingsAreEqual() {
        assertEquals(Reservation.of("AB123", 2), Reservation.of("AB123", 2),
                "records get equals for free");
    }
}
