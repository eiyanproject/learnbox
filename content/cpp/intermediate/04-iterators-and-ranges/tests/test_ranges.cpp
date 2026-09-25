#include "ctest.h"
#include "ranges.h"

#include <vector>

TEST(sums_a_whole_range) {
    std::vector<int> v = {1, 2, 3, 4};
    ASSERT_EQ_INT(10, sum_range(v.begin(), v.end()));
}

TEST(sums_a_partial_range) {
    std::vector<int> v = {1, 2, 3, 4};
    ASSERT_EQ_INT(5, sum_range(v.begin() + 1, v.begin() + 3));
}

TEST(an_empty_range_sums_to_zero) {
    std::vector<int> v = {1, 2};
    ASSERT_EQ_INT(0, sum_range(v.begin(), v.begin()));
}

TEST(sum_range_works_on_a_raw_array) {
    int values[] = {5, 5, 5};
    ASSERT_EQ_INT(15, sum_range(values, values + 3));
}

TEST(remove_all_shortens_the_vector) {
    std::vector<int> v = {1, 2, 3, 2};
    remove_all(v, 2);
    ASSERT_EQ_INT(2, (int)v.size());
    ASSERT_EQ_INT(1, v[0]);
    ASSERT_EQ_INT(3, v[1]);
}

TEST(remove_all_of_something_absent) {
    std::vector<int> v = {1, 2};
    remove_all(v, 99);
    ASSERT_EQ_INT(2, (int)v.size());
}

TEST(remove_all_can_empty_the_vector) {
    std::vector<int> v = {7, 7, 7};
    remove_all(v, 7);
    ASSERT_TRUE(v.empty());
}

TEST(evens_doubled_filters_then_transforms) {
    std::vector<int> v = {1, 2, 3, 4};
    auto out = evens_doubled(v);
    ASSERT_EQ_INT(2, (int)out.size());
    ASSERT_EQ_INT(4, out[0]);
    ASSERT_EQ_INT(8, out[1]);
}

TEST(evens_doubled_leaves_the_source_alone) {
    std::vector<int> v = {1, 2};
    evens_doubled(v);
    ASSERT_EQ_INT(2, (int)v.size());
    ASSERT_EQ_INT(1, v[0]);
}

TEST(evens_doubled_of_nothing) {
    std::vector<int> v;
    ASSERT_TRUE(evens_doubled(v).empty());
}

TEST(count_between_is_inclusive) {
    std::vector<int> v = {1, 5, 10, 15};
    ASSERT_EQ_INT(3, (int)count_between(v, 1, 10));
}

TEST(count_between_matching_nothing) {
    std::vector<int> v = {1, 2};
    ASSERT_EQ_INT(0, (int)count_between(v, 10, 20));
}

CTEST_MAIN
