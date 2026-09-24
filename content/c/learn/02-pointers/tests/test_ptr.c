#include "ctest.h"
#include "ptr.h"

#include <stddef.h>

TEST(swap_exchanges_values) {
    int a = 1, b = 2;
    swap(&a, &b);
    ASSERT_EQ_INT(2, a);
    ASSERT_EQ_INT(1, b);
}

TEST(swap_with_equal_values) {
    int a = 5, b = 5;
    swap(&a, &b);
    ASSERT_EQ_INT(5, a);
    ASSERT_EQ_INT(5, b);
}

TEST(sum_and_count_writes_both) {
    int values[] = {1, 2, 3};
    int sum = 0, count = 0;
    sum_and_count(values, 3, &sum, &count);
    ASSERT_EQ_INT(6, sum);
    ASSERT_EQ_INT(3, count);
}

TEST(sum_and_count_accepts_a_null_sum) {
    int values[] = {1, 2, 3};
    int count = 0;
    sum_and_count(values, 3, NULL, &count);
    ASSERT_EQ_INT(3, count);
}

TEST(sum_and_count_accepts_a_null_count) {
    int values[] = {4, 5};
    int sum = 0;
    sum_and_count(values, 2, &sum, NULL);
    ASSERT_EQ_INT(9, sum);
}

TEST(sum_and_count_accepts_both_null) {
    int values[] = {1};
    sum_and_count(values, 1, NULL, NULL); /* must not crash */
    ASSERT_TRUE(1);
}

TEST(sum_of_an_empty_array) {
    int sum = 99;
    sum_and_count(NULL, 0, &sum, NULL);
    ASSERT_EQ_INT(0, sum);
}

TEST(find_index_finds_it) {
    int values[] = {10, 20, 30};
    ASSERT_EQ_INT(1, find_index(values, 3, 20));
}

TEST(find_index_returns_the_first_match) {
    int values[] = {7, 7};
    ASSERT_EQ_INT(0, find_index(values, 2, 7));
}

TEST(find_index_when_absent) {
    int values[] = {1, 2};
    ASSERT_EQ_INT(-1, find_index(values, 2, 99));
    ASSERT_EQ_INT(-1, find_index(values, 0, 1));
}

TEST(increment_all_changes_the_callers_array) {
    int values[] = {1, 2, 3};
    increment_all(values, 3);
    ASSERT_EQ_INT(2, values[0]);
    ASSERT_EQ_INT(3, values[1]);
    ASSERT_EQ_INT(4, values[2]);
}

TEST(increment_all_of_nothing) {
    int values[] = {5};
    increment_all(values, 0);
    ASSERT_EQ_INT(5, values[0]);
}

CTEST_MAIN
