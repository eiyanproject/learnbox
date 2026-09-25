#include "ctest.h"
#include "ct.h"

#include <array>

TEST(factorial_folds_at_compile_time) {
    /* If factorial were not usable in a constant expression this would not
       compile at all - the static_assert is the proof, not the check below. */
    static_assert(factorial(5) == 120);
    static_assert(factorial(0) == 1);
    ASSERT_EQ_INT(120, factorial(5));
}

TEST(factorial_also_works_at_run_time) {
    int n = 4;
    ASSERT_EQ_INT(24, factorial(n));
}

TEST(fib_at_compile_time) {
    static_assert(fib(0) == 0);
    static_assert(fib(1) == 1);
    static_assert(fib(10) == 55);
    ASSERT_EQ_INT(55, fib(10));
}

TEST(fib_at_run_time) {
    int n = 7;
    ASSERT_EQ_INT(13, fib(n));
}

TEST(length_of_a_literal) {
    static_assert(length("hello") == 5);
    static_assert(length("") == 0);
    ASSERT_EQ_INT(5, (int)length("hello"));
}

TEST(checked_percent_accepts_the_range) {
    constexpr int a = checked_percent(0);
    constexpr int b = checked_percent(50);
    constexpr int c = checked_percent(100);
    ASSERT_EQ_INT(0, a);
    ASSERT_EQ_INT(50, b);
    ASSERT_EQ_INT(100, c);
}

TEST(checked_percent_is_usable_as_an_array_bound) {
    /* Only a genuine constant expression can size an array. */
    int slots[checked_percent(3)] = {1, 2, 3};
    ASSERT_EQ_INT(3, (int)(sizeof(slots) / sizeof(slots[0])));
}

TEST(the_squares_table_is_built_by_the_compiler) {
    constexpr auto table = make_squares<8>();
    static_assert(table.size() == 8);
    static_assert(table[0] == 0);
    static_assert(table[3] == 9);
    static_assert(table[7] == 49);
    ASSERT_EQ_INT(49, table[7]);
}

TEST(a_table_of_one) {
    constexpr auto table = make_squares<1>();
    ASSERT_EQ_INT(1, (int)table.size());
    ASSERT_EQ_INT(0, table[0]);
}

TEST(the_table_is_usable_in_another_constant_expression) {
    constexpr auto table = make_squares<5>();
    static_assert(table[4] == 16);
    constexpr int total = table[0] + table[1] + table[2] + table[3] + table[4];
    ASSERT_EQ_INT(30, total);
}

TEST(a_bigger_table) {
    constexpr auto table = make_squares<16>();
    ASSERT_EQ_INT(225, table[15]);
}

CTEST_MAIN
