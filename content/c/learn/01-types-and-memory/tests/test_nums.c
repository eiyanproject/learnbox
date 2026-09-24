#include "ctest.h"
#include "nums.h"

#include <limits.h>

TEST(char_is_always_one_byte) {
    ASSERT_EQ_INT(1, type_size("char"));
}

TEST(sizes_of_the_usual_types) {
    ASSERT_EQ_INT((int)sizeof(int), type_size("int"));
    ASSERT_EQ_INT((int)sizeof(long), type_size("long"));
    ASSERT_EQ_INT((int)sizeof(double), type_size("double"));
}

TEST(unknown_type_names) {
    ASSERT_EQ_INT(-1, type_size("banana"));
}

TEST(safe_add_of_ordinary_values) {
    int out = 0;
    ASSERT_EQ_INT(1, safe_add(2, 3, &out));
    ASSERT_EQ_INT(5, out);
}

TEST(safe_add_of_negatives) {
    int out = 0;
    ASSERT_EQ_INT(1, safe_add(-2, -3, &out));
    ASSERT_EQ_INT(-5, out);
}

TEST(safe_add_refuses_to_overflow) {
    int out = 12345;
    ASSERT_EQ_INT(0, safe_add(INT_MAX, 1, &out));
    ASSERT_EQ_INT(12345, out); /* out must be left alone */
}

TEST(safe_add_refuses_to_underflow) {
    int out = 12345;
    ASSERT_EQ_INT(0, safe_add(INT_MIN, -1, &out));
    ASSERT_EQ_INT(12345, out);
}

TEST(safe_add_at_the_boundary_still_works) {
    int out = 0;
    ASSERT_EQ_INT(1, safe_add(INT_MAX - 1, 1, &out));
    ASSERT_EQ_INT(INT_MAX, out);
}

TEST(unsigned_addition_wraps_by_definition) {
    ASSERT_EQ_INT(0, (int)wrap_add(UINT_MAX, 1));
}

TEST(unsigned_addition_of_small_values) {
    ASSERT_EQ_INT(7, (int)wrap_add(3, 4));
}

TEST(truncation_keeps_small_values) {
    ASSERT_EQ_INT(100, truncate_to_char(100));
}

TEST(truncation_wraps_above_127) {
    /* 300 & 0xFF is 44, which fits; 200 becomes -56 as a signed char. */
    ASSERT_EQ_INT(44, truncate_to_char(300));
    ASSERT_EQ_INT(-56, truncate_to_char(200));
}

CTEST_MAIN
