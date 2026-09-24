#include "ctest.h"
#include "bag.h"

TEST(evens_keeps_only_even_numbers) {
    auto out = evens_in({1, 2, 3, 4});
    ASSERT_EQ_INT(2, (int)out.size());
    ASSERT_EQ_INT(2, out[0]);
    ASSERT_EQ_INT(4, out[1]);
}

TEST(evens_includes_zero_and_negatives) {
    auto out = evens_in({0, -2, -3});
    ASSERT_EQ_INT(2, (int)out.size());
}

TEST(evens_of_an_empty_vector) {
    ASSERT_TRUE(evens_in({}).empty());
}

TEST(sums_the_values) {
    ASSERT_EQ_INT(10, sum({1, 2, 3, 4}));
}

TEST(sum_of_empty_is_zero) {
    ASSERT_EQ_INT(0, sum({}));
}

TEST(sorted_copy_is_sorted) {
    auto out = sorted_copy({3, 1, 2});
    ASSERT_EQ_INT(1, out[0]);
    ASSERT_EQ_INT(3, out[2]);
}

TEST(sorted_copy_leaves_the_original_alone) {
    std::vector<int> original = {3, 1, 2};
    sorted_copy(original);
    ASSERT_EQ_INT(3, original[0]);
}

TEST(sorted_copy_of_empty) {
    ASSERT_TRUE(sorted_copy({}).empty());
}

TEST(counts_longer_words) {
    ASSERT_EQ_INT(2, count_longer_than({"ada", "grace", "alan"}, 3));
}

TEST(count_is_strictly_greater) {
    ASSERT_EQ_INT(0, count_longer_than({"abc"}, 3));
}

TEST(contains_finds_a_value) {
    ASSERT_TRUE(contains({1, 2, 3}, 2));
}

TEST(contains_reports_absence) {
    ASSERT_FALSE(contains({1, 2, 3}, 99));
    ASSERT_FALSE(contains({}, 1));
}

CTEST_MAIN
