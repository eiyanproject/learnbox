import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;

public class Library {

    public static final int LIMIT = 3;

    // your fields

    public void addBook(String isbn, String title) {
    }

    public List<String> available() {
        return new ArrayList<>();
    }

    public void lend(String isbn, String member) {
    }

    public void giveBack(String isbn) {
    }

    public Optional<String> whoHas(String isbn) {
        return Optional.empty();
    }

    public List<String> borrowedBy(String member) {
        return new ArrayList<>();
    }

    public Map<String, Integer> loanCounts() {
        return new HashMap<>();
    }

    public static void main(String[] args) {
        Library lib = new Library();
        lib.addBook("111", "Dune");
        lib.lend("111", "ana");
        System.out.println(lib.whoHas("111"));
    }
}
