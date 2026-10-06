#include "fraction.h"

#include <numeric>
#include <stdexcept>

Fraction::Fraction(long long numerator, long long denominator) : num_(numerator), den_(denominator) {
    if (den_ == 0) {
        throw std::invalid_argument("denominator is zero");
    }
    if (den_ < 0) {
        num_ = -num_;
        den_ = -den_;
    }
    // gcd(0, d) is d, which turns 0/d into 0/1 with no special case.
    const long long g = std::gcd(num_, den_);
    num_ /= g;
    den_ /= g;
}

std::string Fraction::to_string() const {
    if (den_ == 1) {
        return std::to_string(num_);
    }
    return std::to_string(num_) + "/" + std::to_string(den_);
}

Fraction operator+(const Fraction& a, const Fraction& b) {
    return Fraction(a.numerator() * b.denominator() + b.numerator() * a.denominator(),
                    a.denominator() * b.denominator());
}

Fraction operator-(const Fraction& a, const Fraction& b) {
    return Fraction(a.numerator() * b.denominator() - b.numerator() * a.denominator(),
                    a.denominator() * b.denominator());
}

Fraction operator*(const Fraction& a, const Fraction& b) {
    return Fraction(a.numerator() * b.numerator(), a.denominator() * b.denominator());
}

Fraction operator/(const Fraction& a, const Fraction& b) {
    if (b.numerator() == 0) {
        throw std::invalid_argument("division by zero");
    }
    return Fraction(a.numerator() * b.denominator(), a.denominator() * b.numerator());
}

bool operator==(const Fraction& a, const Fraction& b) {
    return a.numerator() == b.numerator() && a.denominator() == b.denominator();
}

bool operator<(const Fraction& a, const Fraction& b) {
    // Denominators are positive, so cross-multiplying keeps the direction.
    return a.numerator() * b.denominator() < b.numerator() * a.denominator();
}
