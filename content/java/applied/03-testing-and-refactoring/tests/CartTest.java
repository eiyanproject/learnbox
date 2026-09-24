import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class CartTest {

    @Test
    void anEmptyCartHasNothingInIt() {
        Cart cart = new Cart();
        assertEquals(0, cart.itemCount());
        assertEquals(0.0, cart.total(), 0.001);
    }

    @Test
    void addingItemsCountsTheQuantity() {
        Cart cart = new Cart();
        cart.addItem("apple", 2, 1.50);
        cart.addItem("pear", 1, 2.00);
        assertEquals(3, cart.itemCount(), "itemCount is the total quantity, not the line count");
    }

    @Test
    void addingTheSameNameIncreasesTheQuantity() {
        Cart cart = new Cart();
        cart.addItem("apple", 2, 1.50);
        cart.addItem("apple", 3, 1.50);
        assertEquals(5, cart.itemCount());
    }

    @Test
    void subtotalMultipliesQuantityByPrice() {
        Cart cart = new Cart();
        cart.addItem("apple", 2, 1.50);
        cart.addItem("pear", 1, 2.00);
        assertEquals(5.00, cart.subtotal(), 0.001);
    }

    @Test
    void quantityMustBePositive() {
        Cart cart = new Cart();
        assertThrows(IllegalArgumentException.class, () -> cart.addItem("apple", 0, 1.0));
        assertThrows(IllegalArgumentException.class, () -> cart.addItem("apple", -1, 1.0));
    }

    @Test
    void totalWithoutACouponIsTheSubtotal() {
        Cart cart = new Cart();
        cart.addItem("apple", 2, 1.50);
        assertEquals(3.00, cart.total(), 0.001);
    }

    @Test
    void save10TakesTenPercent() {
        Cart cart = new Cart();
        cart.addItem("apple", 2, 1.50);
        cart.applyCoupon("SAVE10");
        assertEquals(2.70, cart.total(), 0.001);
    }

    @Test
    void halfTakesFiftyPercent() {
        Cart cart = new Cart();
        cart.addItem("apple", 2, 1.50);
        cart.applyCoupon("HALF");
        assertEquals(1.50, cart.total(), 0.001);
    }

    @Test
    void anUnknownCouponIsRejected() {
        Cart cart = new Cart();
        assertThrows(IllegalArgumentException.class, () -> cart.applyCoupon("FREESTUFF"));
    }

    @Test
    void theTotalIsRoundedToTwoDecimals() {
        Cart cart = new Cart();
        cart.addItem("thing", 3, 0.335);   // 1.005 before discount
        assertEquals(1.01, cart.total(), 0.0001);
    }

    @Test
    void addingAfterACouponStillDiscounts() {
        Cart cart = new Cart();
        cart.applyCoupon("HALF");
        cart.addItem("apple", 2, 1.00);
        assertEquals(1.00, cart.total(), 0.001);
    }
}
