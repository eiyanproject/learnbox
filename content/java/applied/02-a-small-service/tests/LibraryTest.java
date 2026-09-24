import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class LibraryTest {

    private static LibraryService service() {
        return new LibraryService(new InMemoryStore());
    }

    private static final Book DUNE = new Book("Dune", "Herbert", 1965);
    private static final Book MESSIAH = new Book("Dune Messiah", "Herbert", 1969);
    private static final Book NEUROMANCER = new Book("Neuromancer", "Gibson", 1984);

    @Test
    void addAndCount() {
        LibraryService s = service();
        s.add(DUNE);
        assertEquals(1, s.count());
    }

    @Test
    void findReturnsTheBook() {
        LibraryService s = service();
        s.add(DUNE);
        assertEquals(Optional.of(DUNE), s.find("Dune"));
    }

    @Test
    void findOnAMissingTitleIsEmpty() {
        assertTrue(service().find("Nothing").isEmpty());
    }

    @Test
    void duplicateTitlesAreRejected() {
        LibraryService s = service();
        s.add(DUNE);
        assertThrows(IllegalStateException.class, () -> s.add(DUNE));
        assertEquals(1, s.count(), "the rejected add must not have stored anything");
    }

    @Test
    void groupsTitlesByAuthor() {
        LibraryService s = service();
        s.add(DUNE);
        s.add(MESSIAH);
        s.add(NEUROMANCER);
        Map<String, List<String>> byAuthor = s.titlesByAuthor();
        assertEquals(List.of("Dune", "Dune Messiah"), byAuthor.get("Herbert"));
        assertEquals(List.of("Neuromancer"), byAuthor.get("Gibson"));
    }

    @Test
    void theStoreKeepsInsertionOrder() {
        BookStore store = new InMemoryStore();
        store.save(NEUROMANCER);
        store.save(DUNE);
        assertEquals(List.of(NEUROMANCER, DUNE), store.all());
    }

    @Test
    void theServiceWorksWithAnyStoreImplementation() {
        // The point of the interface: a different implementation, no change
        // to the service.
        BookStore counting = new BookStore() {
            private final BookStore inner = new InMemoryStore();
            int saves;

            @Override
            public void save(Book book) {
                saves++;
                inner.save(book);
            }

            @Override
            public Optional<Book> findByTitle(String title) {
                return inner.findByTitle(title);
            }

            @Override
            public List<Book> all() {
                return inner.all();
            }
        };
        LibraryService s = new LibraryService(counting);
        s.add(DUNE);
        assertEquals(1, s.count());
    }

    @Test
    void aBlankTitleIsRejectedByTheModel() {
        assertThrows(IllegalArgumentException.class, () -> new Book("", "x", 2000));
    }

    @Test
    void anEmptyServiceGroupsToAnEmptyMap() {
        assertTrue(service().titlesByAuthor().isEmpty());
    }
}
