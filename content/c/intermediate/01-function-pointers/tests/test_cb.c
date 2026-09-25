#include "ctest.h"
#include "cb.h"

#include <limits.h>
#include <stddef.h>

static int double_it(int n) { return n * 2; }

TEST(the_operations_work) {
    ASSERT_EQ_INT(5, add_op(2, 3));
    ASSERT_EQ_INT(-1, sub_op(2, 3));
    ASSERT_EQ_INT(6, mul_op(2, 3));
}

TEST(find_op_returns_a_callable_pointer) {
    BinaryOp op = find_op("add");
    ASSERT_NOT_NULL((void *)op);
    ASSERT_EQ_INT(7, op(3, 4));
}

TEST(find_op_distinguishes_the_entries) {
    ASSERT_EQ_INT(12, find_op("mul")(3, 4));
    ASSERT_EQ_INT(-1, find_op("sub")(3, 4));
}

TEST(find_op_on_an_unknown_name) {
    ASSERT_NULL((void *)find_op("divide"));
}

TEST(apply_all_transforms_in_place) {
    int values[] = {1, 2, 3};
    apply_all(values, 3, double_it);
    ASSERT_EQ_INT(2, values[0]);
    ASSERT_EQ_INT(6, values[2]);
}

TEST(apply_all_of_nothing) {
    int values[] = {5};
    apply_all(values, 0, double_it);
    ASSERT_EQ_INT(5, values[0]);
}

TEST(reduce_sums) {
    int values[] = {1, 2, 3};
    ASSERT_EQ_INT(6, reduce(values, 3, 0, add_op));
}

TEST(reduce_uses_the_initial_value) {
    int values[] = {1, 2, 3};
    ASSERT_EQ_INT(16, reduce(values, 3, 10, add_op));
}

TEST(reduce_multiplies_too) {
    int values[] = {2, 3, 4};
    ASSERT_EQ_INT(24, reduce(values, 3, 1, mul_op));
}

TEST(reduce_of_nothing_is_the_initial) {
    ASSERT_EQ_INT(42, reduce(NULL, 0, 42, add_op));
}

TEST(sort_orders_ascending) {
    int values[] = {3, 1, 2};
    sort_ints(values, 3);
    ASSERT_EQ_INT(1, values[0]);
    ASSERT_EQ_INT(3, values[2]);
}

TEST(sort_handles_extreme_values) {
    /* A comparator written as x - y overflows here and sorts them wrongly. */
    int values[] = {INT_MAX, INT_MIN, 0};
    sort_ints(values, 3);
    ASSERT_EQ_INT(INT_MIN, values[0]);
    ASSERT_EQ_INT(0, values[1]);
    ASSERT_EQ_INT(INT_MAX, values[2]);
}

CTEST_MAIN
