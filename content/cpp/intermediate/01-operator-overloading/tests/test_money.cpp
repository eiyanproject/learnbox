#include "ctest.h"
#include "money.h"

#include <sstream>

TEST(construction_and_access) {
    ASSERT_EQ_INT(1234, (int)Money(1234).cents());
}

TEST(a_default_money_is_zero) {
    ASSERT_EQ_INT(0, (int)Money().cents());
}

TEST(plus_equals_modifies) {
    Money m(100);
    m += Money(50);
    ASSERT_EQ_INT(150, (int)m.cents());
}

TEST(plus_equals_chains) {
    Money a(1), b(2), c(3);
    a += b += c;
    ASSERT_EQ_INT(5, (int)b.cents());
    ASSERT_EQ_INT(6, (int)a.cents());
}

TEST(plus_does_not_modify_its_operands) {
    Money a(100), b(50);
    Money sum = a + b;
    ASSERT_EQ_INT(150, (int)sum.cents());
    ASSERT_EQ_INT(100, (int)a.cents());
    ASSERT_EQ_INT(50, (int)b.cents());
}

TEST(minus_works) {
    ASSERT_EQ_INT(50, (int)(Money(100) - Money(50)).cents());
}

TEST(multiplication_works_in_both_orders) {
    /* A member operator* could only provide the first of these. */
    ASSERT_EQ_INT(300, (int)(Money(100) * 3).cents());
    ASSERT_EQ_INT(300, (int)(3 * Money(100)).cents());
}

TEST(equality_is_by_value) {
    ASSERT_TRUE(Money(100) == Money(100));
    ASSERT_TRUE(Money(100) != Money(50));
}

TEST(ordering_comes_from_the_spaceship) {
    ASSERT_TRUE(Money(50) < Money(100));
    ASSERT_TRUE(Money(100) > Money(50));
    ASSERT_TRUE(Money(100) <= Money(100));
    ASSERT_TRUE(Money(100) >= Money(100));
}

TEST(streaming_formats_as_currency) {
    std::ostringstream out;
    out << Money(1234);
    ASSERT_STR_EQ("$12.34", out.str().c_str());
}

TEST(streaming_pads_the_cents) {
    std::ostringstream out;
    out << Money(1205);
    ASSERT_STR_EQ("$12.05", out.str().c_str());
}

TEST(streaming_chains) {
    std::ostringstream out;
    out << Money(100) << " and " << Money(200);
    ASSERT_STR_EQ("$1.00 and $2.00", out.str().c_str());
}

CTEST_MAIN
