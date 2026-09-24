#include "ctest.h"
#include "dyn.h"

#include <stdlib.h>
#include <string.h>

TEST(make_range_fills_zero_upwards) {
    int *r = make_range(4);
    ASSERT_NOT_NULL(r);
    ASSERT_EQ_INT(0, r[0]);
    ASSERT_EQ_INT(3, r[3]);
    free(r);
}

TEST(make_range_of_one) {
    int *r = make_range(1);
    ASSERT_NOT_NULL(r);
    ASSERT_EQ_INT(0, r[0]);
    free(r);
}

TEST(make_range_rejects_non_positive) {
    ASSERT_NULL(make_range(0));
    ASSERT_NULL(make_range(-3));
}

TEST(dup_string_copies_the_contents) {
    char *copy = dup_string("ada");
    ASSERT_NOT_NULL(copy);
    ASSERT_STR_EQ("ada", copy);
    free(copy);
}

TEST(dup_string_is_a_separate_buffer) {
    const char *original = "ada";
    char *copy = dup_string(original);
    ASSERT_TRUE(copy != original);
    free(copy);
}

TEST(dup_string_of_empty) {
    char *copy = dup_string("");
    ASSERT_NOT_NULL(copy);
    ASSERT_EQ_INT(0, copy[0]);
    free(copy);
}

TEST(dup_string_of_null) {
    ASSERT_NULL(dup_string(NULL));
}

TEST(grow_keeps_the_existing_values) {
    int *r = make_range(3);
    r = grow_array(r, 3, 6);
    ASSERT_NOT_NULL(r);
    ASSERT_EQ_INT(0, r[0]);
    ASSERT_EQ_INT(2, r[2]);
    free(r);
}

TEST(grow_zeroes_the_new_slots) {
    int *r = make_range(3);
    r = grow_array(r, 3, 6);
    ASSERT_EQ_INT(0, r[3]);
    ASSERT_EQ_INT(0, r[5]);
    free(r);
}

TEST(grow_from_null_allocates) {
    int *r = grow_array(NULL, 0, 4);
    ASSERT_NOT_NULL(r);
    ASSERT_EQ_INT(0, r[0]);
    free(r);
}

TEST(sum_and_free_totals) {
    ASSERT_EQ_INT(0 + 1 + 2 + 3, sum_and_free(make_range(4), 4));
}

TEST(sum_and_free_of_null_is_zero) {
    ASSERT_EQ_INT(0, sum_and_free(NULL, 0));
}

CTEST_MAIN
