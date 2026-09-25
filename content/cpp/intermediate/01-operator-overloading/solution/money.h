#ifndef MONEY_H
#define MONEY_H

#include <compare>
#include <iomanip>
#include <ostream>

class Money {
public:
    explicit Money(long cents = 0) : cents_(cents) {}

    long cents() const { return cents_; }

    // Modifying operators are members, and return *this so they chain.
    Money& operator+=(const Money& rhs) {
        cents_ += rhs.cents_;
        return *this;
    }

    Money& operator-=(const Money& rhs) {
        cents_ -= rhs.cents_;
        return *this;
    }

    Money& operator*=(long factor) {
        cents_ *= factor;
        return *this;
    }

    // C++20: one line each, and != and the relational operators follow.
    bool operator==(const Money&) const = default;
    std::strong_ordering operator<=>(const Money&) const = default;

private:
    long cents_;
};

// Free functions, so both operands are treated alike. The left one is taken
// by value because that copy becomes the result.
inline Money operator+(Money lhs, const Money& rhs) {
    lhs += rhs;
    return lhs;
}

inline Money operator-(Money lhs, const Money& rhs) {
    lhs -= rhs;
    return lhs;
}

inline Money operator*(Money lhs, long factor) {
    lhs *= factor;
    return lhs;
}

// The other order, which a member operator* could not provide.
inline Money operator*(long factor, Money rhs) {
    rhs *= factor;
    return rhs;
}

inline std::ostream& operator<<(std::ostream& out, const Money& money) {
    long cents = money.cents();
    const char* sign = cents < 0 ? "-" : "";
    long abs_cents = cents < 0 ? -cents : cents;
    return out << sign << "$" << abs_cents / 100 << "."
               << std::setw(2) << std::setfill('0') << abs_cents % 100;
}

#endif
