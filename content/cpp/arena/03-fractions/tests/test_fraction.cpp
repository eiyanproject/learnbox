#include "ctest.h"
#include "fraction.h"

#include <stdexcept>

static bool holds(const Fraction& f, long long n, long long d) {
    return f.numerator() == n && f.denominator() == d;
}

template <typename F>
static bool throws_invalid(F f) {
    try {
        f();
    } catch (const std::invalid_argument&) {
        return true;
    } catch (...) {
        return false;
    }
    return false;
}

TEST(stores_what_it_is_given) {
    ASSERT_TRUE(holds(Fraction(3, 4), 3, 4));
    ASSERT_TRUE(holds(Fraction(5), 5, 1));
}

TEST(reduces_to_lowest_terms) {
    ASSERT_TRUE(holds(Fraction(2, 4), 1, 2));
    ASSERT_TRUE(holds(Fraction(100, 25), 4, 1));
    ASSERT_TRUE(holds(Fraction(17, 51), 1, 3));
}

TEST(the_sign_lives_on_the_numerator) {
    ASSERT_TRUE(holds(Fraction(1, -2), -1, 2));
    ASSERT_TRUE(holds(Fraction(-1, -2), 1, 2));
    ASSERT_TRUE(holds(Fraction(-6, 8), -3, 4));
}

TEST(zero_is_always_zero_over_one) {
    ASSERT_TRUE(holds(Fraction(0, 5), 0, 1));
    ASSERT_TRUE(holds(Fraction(0, -7), 0, 1));
    ASSERT_TRUE(holds(Fraction(0), 0, 1));
}

TEST(a_zero_denominator_is_refused) {
    ASSERT_TRUE(throws_invalid([] { Fraction(1, 0); }));
    ASSERT_TRUE(throws_invalid([] { Fraction(0, 0); }));
}

TEST(addition) {
    ASSERT_TRUE(holds(Fraction(1, 2) + Fraction(1, 3), 5, 6));
    ASSERT_TRUE(holds(Fraction(1, 4) + Fraction(1, 4), 1, 2));
    ASSERT_TRUE(holds(Fraction(1, 2) + Fraction(-1, 2), 0, 1));
}

TEST(subtraction) {
    ASSERT_TRUE(holds(Fraction(1, 2) - Fraction(1, 3), 1, 6));
    ASSERT_TRUE(holds(Fraction(1, 3) - Fraction(1, 2), -1, 6));
}

TEST(multiplication) {
    ASSERT_TRUE(holds(Fraction(1, 2) * Fraction(1, 3), 1, 6));
    ASSERT_TRUE(holds(Fraction(2, 3) * Fraction(3, 2), 1, 1));
    ASSERT_TRUE(holds(Fraction(-2, 3) * Fraction(3, 4), -1, 2));
}

TEST(division) {
    ASSERT_TRUE(holds(Fraction(1, 2) / Fraction(1, 3), 3, 2));
    ASSERT_TRUE(holds(Fraction(1, 2) / Fraction(-1, 4), -2, 1));
}

TEST(dividing_by_zero_is_refused) {
    ASSERT_TRUE(throws_invalid([] { Fraction(1, 2) / Fraction(0); }));
}

TEST(whole_numbers_convert) {
    ASSERT_TRUE(holds(Fraction(1, 2) + 1, 3, 2));
    ASSERT_TRUE(holds(Fraction(3, 4) * 4, 3, 1));
}

TEST(equality_is_by_value) {
    ASSERT_TRUE(Fraction(1, 2) == Fraction(2, 4));
    ASSERT_TRUE(Fraction(-1, 2) == Fraction(1, -2));
    ASSERT_FALSE(Fraction(1, 2) == Fraction(1, 3));
    ASSERT_TRUE(Fraction(0, 3) == Fraction(0, 9));
}

TEST(ordering_is_by_value) {
    ASSERT_TRUE(Fraction(1, 3) < Fraction(1, 2));
    ASSERT_FALSE(Fraction(1, 2) < Fraction(1, 3));
    ASSERT_FALSE(Fraction(1, 2) < Fraction(2, 4));
    ASSERT_TRUE(Fraction(-1, 2) < Fraction(1, 3));
    ASSERT_TRUE(Fraction(-1, 2) < Fraction(-1, 3));
}

TEST(to_string) {
    ASSERT_STR_EQ("3/4", Fraction(3, 4).to_string().c_str());
    ASSERT_STR_EQ("-3/4", Fraction(6, -8).to_string().c_str());
    ASSERT_STR_EQ("2", Fraction(4, 2).to_string().c_str());
    ASSERT_STR_EQ("0", Fraction(0, 9).to_string().c_str());
    ASSERT_STR_EQ("-5", Fraction(-5).to_string().c_str());
}

TEST(a_sum_that_stays_exact) {
    Fraction total(0);
    for (int i = 0; i < 30; i++) {
        total = total + Fraction(1, 3);
    }
    ASSERT_TRUE(holds(total, 10, 1));
}

CTEST_MAIN
