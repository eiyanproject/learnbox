#ifndef FRACTION_H
#define FRACTION_H

#include <string>

class Fraction {
public:
    Fraction(long long numerator, long long denominator = 1);

    long long numerator() const { return num_; }
    long long denominator() const { return den_; }

    std::string to_string() const;

private:
    long long num_;
    long long den_;
};

Fraction operator+(const Fraction& a, const Fraction& b);
Fraction operator-(const Fraction& a, const Fraction& b);
Fraction operator*(const Fraction& a, const Fraction& b);
Fraction operator/(const Fraction& a, const Fraction& b);
bool operator==(const Fraction& a, const Fraction& b);
bool operator<(const Fraction& a, const Fraction& b);

#endif
