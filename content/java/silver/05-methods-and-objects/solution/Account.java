public class Account {

    private final String owner;
    private double balance;

    public Account(String owner, double balance) {
        this.owner = owner;
        this.balance = balance;
    }

    public Account(String owner) {
        this(owner, 0);
    }

    public String getOwner() {
        return owner;
    }

    public double getBalance() {
        return balance;
    }

    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("deposit must be positive");
        }
        balance += amount;
    }

    public void withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("withdrawal must be positive");
        }
        if (amount > balance) {
            throw new IllegalArgumentException("insufficient funds");
        }
        balance -= amount;
    }

    public void transferTo(Account other, double amount) {
        withdraw(amount);
        other.deposit(amount);
    }

    public static void main(String[] args) {
        Account a = new Account("ada", 100);
        Account b = new Account("bob");
        a.transferTo(b, 25);
        System.out.println(a.getBalance() + " " + b.getBalance());
    }
}
