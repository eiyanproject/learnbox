public class Booking {

    public static void main(String[] args) {
        Reservation r = Reservation.of("AB123", 2);
        System.out.println(r.confirm());
    }
}

enum Status {
    PENDING,
    CONFIRMED,
    CANCELLED;

    public boolean isFinal() {
        return this == CANCELLED;
    }
}

record Reservation(String reference, int guests, Status status) {

    Reservation {
        if (reference == null || reference.isBlank()) {
            throw new IllegalArgumentException("reference must not be blank");
        }
        if (guests < 1) {
            throw new IllegalArgumentException("at least one guest");
        }
    }

    static Reservation of(String reference, int guests) {
        return new Reservation(reference, guests, Status.PENDING);
    }

    Reservation confirm() {
        return new Reservation(reference, guests, Status.CONFIRMED);
    }

    Reservation cancel() {
        return new Reservation(reference, guests, Status.CANCELLED);
    }
}
