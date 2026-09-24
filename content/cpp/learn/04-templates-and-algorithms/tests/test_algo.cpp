#include "ctest.h"
#include "algo.h"

#include <stdexcept>
#include <string>
#include <vector>

TEST(largest_of_ints) {
    ASSERT_EQ_INT(9, largest<int>({3, 9, 4}));
}

TEST(largest_of_negatives) {
    ASSERT_EQ_INT(-2, largest<int>({-5, -2, -9}));
}

TEST(largest_works_for_strings_too) {
    // The same template, a different type: this is the point of it.
    ASSERT_STR_EQ("pear", largest<std::string>({"apple", "pear", "fig"}).c_str());
}

TEST(largest_of_empty_throws) {
    bool threw = false;
    try {
        largest<int>({});
    } catch (const std::invalid_argument&) {
        threw = true;
    }
    ASSERT_TRUE(threw);
}

TEST(count_if_with_a_lambda) {
    std::vector<int> v = {1, 2, 3, 4};
    ASSERT_EQ_INT(2, count_if_matching(v, [](int n) { return n % 2 == 0; }));
}

TEST(count_if_capturing_a_variable) {
    std::vector<int> v = {1, 5, 9};
    int threshold = 4;
    ASSERT_EQ_INT(2, count_if_matching(v, [threshold](int n) { return n > threshold; }));
}

TEST(count_if_matching_nothing) {
    std::vector<int> v = {1, 3};
    ASSERT_EQ_INT(0, count_if_matching(v, [](int n) { return n > 100; }));
}

TEST(transform_doubles_every_element) {
    std::vector<int> v = {1, 2, 3};
    auto out = transform_all(v, [](int n) { return n * 2; });
    ASSERT_EQ_INT(3, (int)out.size());
    ASSERT_EQ_INT(2, out[0]);
    ASSERT_EQ_INT(6, out[2]);
}

TEST(transform_can_change_the_type) {
    std::vector<int> v = {1, 2};
    auto out = transform_all(v, [](int n) { return std::to_string(n); });
    ASSERT_STR_EQ("1", out[0].c_str());
    ASSERT_STR_EQ("2", out[1].c_str());
}

TEST(sum_of_ints) {
    ASSERT_EQ_INT(6, sum_all<int>({1, 2, 3}, 0));
}

TEST(sum_with_a_starting_value) {
    ASSERT_EQ_INT(16, sum_all<int>({1, 2, 3}, 10));
}

TEST(sum_concatenates_strings) {
    ASSERT_STR_EQ("abc", sum_all<std::string>({"a", "b", "c"}, "").c_str());
}

CTEST_MAIN
