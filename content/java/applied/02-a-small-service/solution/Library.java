import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class Library {

    public static void main(String[] args) {
        LibraryService service = new LibraryService(new InMemoryStore());
        service.add(new Book("Dune", "Herbert", 1965));
        System.out.println(service.count());
    }
}

record Book(String title, String author, int year) {

    Book {
        if (title == null || title.isBlank()) {
            throw new IllegalArgumentException("title must not be blank");
        }
    }
}

interface BookStore {

    void save(Book book);

    Optional<Book> findByTitle(String title);

    List<Book> all();
}

class InMemoryStore implements BookStore {

    private final Map<String, Book> books = new LinkedHashMap<>();

    @Override
    public void save(Book book) {
        books.put(book.title(), book);
    }

    @Override
    public Optional<Book> findByTitle(String title) {
        return Optional.ofNullable(books.get(title));
    }

    @Override
    public List<Book> all() {
        return new ArrayList<>(books.values());
    }
}

class LibraryService {

    private final BookStore store;

    LibraryService(BookStore store) {
        this.store = store;
    }

    void add(Book book) {
        if (store.findByTitle(book.title()).isPresent()) {
            throw new IllegalStateException("already have " + book.title());
        }
        store.save(book);
    }

    Optional<Book> find(String title) {
        return store.findByTitle(title);
    }

    int count() {
        return store.all().size();
    }

    Map<String, List<String>> titlesByAuthor() {
        return store.all().stream()
                .collect(Collectors.groupingBy(Book::author,
                        Collectors.mapping(Book::title, Collectors.toList())));
    }
}
