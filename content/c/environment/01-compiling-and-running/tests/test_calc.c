#include "ctest.h"
#include "calc.h"

TEST(max_picks_the_larger) {
    ASSERT_EQ_INT(5, c_max(3, 5));
    ASSERT_EQ_INT(5, c_max(5, 3));
}

TEST(max_of_equal_values) {
    ASSERT_EQ_INT(4, c_max(4, 4));
}

TEST(max_handles_negatives) {
    ASSERT_EQ_INT(-2, c_max(-5, -2));
}

TEST(clamp_pins_below) {
    ASSERT_EQ_INT(0, clamp(-5, 0, 10));
}

TEST(clamp_pins_above) {
    ASSERT_EQ_INT(10, clamp(50, 0, 10));
}

TEST(clamp_leaves_values_inside_alone) {
    ASSERT_EQ_INT(7, clamp(7, 0, 10));
}

TEST(clamp_boundaries_are_inclusive) {
    ASSERT_EQ_INT(0, clamp(0, 0, 10));
    ASSERT_EQ_INT(10, clamp(10, 0, 10));
}

TEST(even_numbers) {
    ASSERT_TRUE(is_even(0));
    ASSERT_TRUE(is_even(2));
    ASSERT_FALSE(is_even(3));
}

TEST(even_works_for_negatives) {
    /* -3 % 2 is -1 in C, so comparing against 1 would be wrong. */
    ASSERT_TRUE(is_even(-4));
    ASSERT_FALSE(is_even(-3));
}

TEST(sign_of_each_case) {
    ASSERT_STR_EQ("negative", sign_of(-1));
    ASSERT_STR_EQ("zero", sign_of(0));
    ASSERT_STR_EQ("positive", sign_of(1));
}

CTEST_MAIN
