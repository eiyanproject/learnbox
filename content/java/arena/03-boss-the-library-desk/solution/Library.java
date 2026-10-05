import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;

public class Library {

    public static final int LIMIT = 3;

    private final Map<String, String> titles = new HashMap<>();   // isbn -> title
    private final Map<String, String> loans = new HashMap<>();    // isbn -> member

    public void addBook(String isbn, String title) {
        if (titles.containsKey(isbn)) {
            throw new IllegalArgumentException("already have " + isbn);
        }
        titles.put(isbn, title);
    }

    public List<String> available() {
        List<String> out = new ArrayList<>();
        for (Map.Entry<String, String> book : titles.entrySet()) {
            if (!loans.containsKey(book.getKey())) {
                out.add(book.getValue());
            }
        }
        Collections.sort(out);
        return out;
    }

    private void mustExist(String isbn) {
        if (!titles.containsKey(isbn)) {
            throw new NoSuchElementException("no book " + isbn);
        }
    }

    public void lend(String isbn, String member) {
        mustExist(isbn);
        if (loans.containsKey(isbn)) {
            throw new IllegalStateException(isbn + " is already on loan");
        }
        if (loanCounts().getOrDefault(member, 0) >= LIMIT) {
            throw new IllegalStateException(member + " has " + LIMIT + " books already");
        }
        loans.put(isbn, member);
    }

    public void giveBack(String isbn) {
        mustExist(isbn);
        if (loans.remove(isbn) == null) {
            throw new IllegalStateException(isbn + " is not on loan");
        }
    }

    public Optional<String> whoHas(String isbn) {
        mustExist(isbn);
        return Optional.ofNullable(loans.get(isbn));
    }

    public List<String> borrowedBy(String member) {
        List<String> out = new ArrayList<>();
        for (Map.Entry<String, String> loan : loans.entrySet()) {
            if (loan.getValue().equals(member)) {
                out.add(titles.get(loan.getKey()));
            }
        }
        Collections.sort(out);
        return out;
    }

    public Map<String, Integer> loanCounts() {
        Map<String, Integer> out = new HashMap<>();
        for (String member : loans.values()) {
            out.merge(member, 1, Integer::sum);
        }
        return out;
    }

    public static void main(String[] args) {
        Library lib = new Library();
        lib.addBook("111", "Dune");
        lib.lend("111", "ana");
        System.out.println(lib.whoHas("111"));
    }
}
