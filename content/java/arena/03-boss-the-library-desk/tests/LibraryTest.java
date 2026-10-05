import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class LibraryTest {

    private Library lib;

    @BeforeEach
    void shelve() {
        lib = new Library();
        lib.addBook("111", "Dune");
        lib.addBook("222", "Emma");
        lib.addBook("333", "Ulysses");
        lib.addBook("444", "Beloved");
        lib.addBook("555", "Carrie");
    }

    @Test
    void everythingStartsOnTheShelf() {
        assertEquals(List.of("Beloved", "Carrie", "Dune", "Emma", "Ulysses"), lib.available());
        assertEquals(Optional.empty(), lib.whoHas("111"));
        assertTrue(lib.loanCounts().isEmpty());
    }

    @Test
    void anEmptyLibrary() {
        Library empty = new Library();
        assertTrue(empty.available().isEmpty());
        assertTrue(empty.borrowedBy("ana").isEmpty());
        assertTrue(empty.loanCounts().isEmpty());
    }

    @Test
    void aDuplicateIsbnIsRefused() {
        assertThrows(IllegalArgumentException.class, () -> lib.addBook("111", "Dune, again"));
        assertEquals(5, lib.available().size());
        assertTrue(lib.available().contains("Dune"));
    }

    @Test
    void twoCopiesOfATitleAreTwoBooks() {
        lib.addBook("999", "Dune");
        lib.lend("111", "ana");
        assertTrue(lib.available().contains("Dune"));
        assertEquals(5, lib.available().size());
    }

    @Test
    void lending() {
        lib.lend("111", "ana");
        assertEquals(Optional.of("ana"), lib.whoHas("111"));
        assertEquals(List.of("Beloved", "Carrie", "Emma", "Ulysses"), lib.available());
        assertEquals(List.of("Dune"), lib.borrowedBy("ana"));
    }

    @Test
    void borrowedTitlesAreSorted() {
        lib.lend("333", "ana");
        lib.lend("111", "ana");
        lib.lend("222", "bo");
        assertEquals(List.of("Dune", "Ulysses"), lib.borrowedBy("ana"));
        assertEquals(List.of("Emma"), lib.borrowedBy("bo"));
        assertTrue(lib.borrowedBy("nobody").isEmpty());
    }

    @Test
    void anUnknownBookCannotBeLent() {
        assertThrows(NoSuchElementException.class, () -> lib.lend("000", "ana"));
        assertTrue(lib.loanCounts().isEmpty());
    }

    @Test
    void aBookOnLoanCannotBeLentAgain() {
        lib.lend("111", "ana");
        assertThrows(IllegalStateException.class, () -> lib.lend("111", "bo"));
        assertThrows(IllegalStateException.class, () -> lib.lend("111", "ana"));
        assertEquals(Optional.of("ana"), lib.whoHas("111"));
    }

    @Test
    void threeBooksIsTheLimit() {
        assertEquals(3, Library.LIMIT);
        lib.lend("111", "ana");
        lib.lend("222", "ana");
        lib.lend("333", "ana");
        assertThrows(IllegalStateException.class, () -> lib.lend("444", "ana"));
        assertEquals(Optional.empty(), lib.whoHas("444"));
        lib.lend("444", "bo");
        assertEquals(Optional.of("bo"), lib.whoHas("444"));
    }

    @Test
    void returningABookMakesRoom() {
        lib.lend("111", "ana");
        lib.lend("222", "ana");
        lib.lend("333", "ana");
        lib.giveBack("222");
        lib.lend("444", "ana");
        assertEquals(List.of("Beloved", "Dune", "Ulysses"), lib.borrowedBy("ana"));
        assertEquals(List.of("Carrie", "Emma"), lib.available());
    }

    @Test
    void anUnknownBookIsCheckedBeforeTheLimit() {
        lib.lend("111", "ana");
        lib.lend("222", "ana");
        lib.lend("333", "ana");
        assertThrows(NoSuchElementException.class, () -> lib.lend("000", "ana"));
    }

    @Test
    void givingBack() {
        lib.lend("111", "ana");
        lib.giveBack("111");
        assertEquals(Optional.empty(), lib.whoHas("111"));
        assertTrue(lib.borrowedBy("ana").isEmpty());
        lib.lend("111", "bo");
        assertEquals(Optional.of("bo"), lib.whoHas("111"));
    }

    @Test
    void givingBackWhatWasNotLent() {
        assertThrows(IllegalStateException.class, () -> lib.giveBack("111"));
        assertThrows(NoSuchElementException.class, () -> lib.giveBack("000"));
    }

    @Test
    void whoHasAnUnknownBook() {
        assertThrows(NoSuchElementException.class, () -> lib.whoHas("000"));
    }

    @Test
    void loanCounts() {
        lib.lend("111", "ana");
        lib.lend("222", "ana");
        lib.lend("333", "bo");
        assertEquals(Map.of("ana", 2, "bo", 1), lib.loanCounts());
        lib.giveBack("333");
        assertEquals(Map.of("ana", 2), lib.loanCounts());
    }

    @Test
    void whatComesBackIsACopy() {
        lib.lend("111", "ana");
        // An unmodifiable copy is as good as a modifiable one.
        try {
            lib.available().clear();
            lib.borrowedBy("ana").clear();
            lib.loanCounts().clear();
        } catch (UnsupportedOperationException ignored) {
        }
        assertEquals(4, lib.available().size());
        assertEquals(List.of("Dune"), lib.borrowedBy("ana"));
        assertEquals(Map.of("ana", 1), lib.loanCounts());
    }

    @Test
    void twoLibrariesDoNotShare() {
        Library other = new Library();
        other.addBook("111", "Dune");
        other.lend("111", "cy");
        assertEquals(Optional.empty(), lib.whoHas("111"));
        assertEquals(Optional.of("cy"), other.whoHas("111"));
    }
}
