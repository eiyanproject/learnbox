#include "ctest.h"
#include "intervals.h"

using V = std::vector<Interval>;

TEST(overlapping_intervals_merge) {
    ASSERT_TRUE((merge_intervals({{1, 3}, {2, 6}, {8, 10}}) == V{{1, 6}, {8, 10}}));
}

TEST(touching_intervals_merge) {
    ASSERT_TRUE((merge_intervals({{1, 3}, {3, 5}}) == V{{1, 5}}));
}

TEST(close_is_not_touching) {
    ASSERT_TRUE((merge_intervals({{1, 2}, {3, 4}}) == V{{1, 2}, {3, 4}}));
}

TEST(any_order_in_sorted_out) {
    ASSERT_TRUE((merge_intervals({{5, 7}, {1, 3}, {3, 5}}) == V{{1, 7}}));
    ASSERT_TRUE((merge_intervals({{20, 30}, {1, 2}, {10, 11}}) == V{{1, 2}, {10, 11}, {20, 30}}));
}

TEST(an_interval_inside_another_disappears) {
    ASSERT_TRUE((merge_intervals({{1, 10}, {2, 3}, {4, 5}}) == V{{1, 10}}));
    ASSERT_TRUE((merge_intervals({{2, 3}, {1, 10}}) == V{{1, 10}}));
}

TEST(a_chain_collapses_into_one) {
    ASSERT_TRUE((merge_intervals({{1, 2}, {2, 3}, {3, 4}, {4, 5}}) == V{{1, 5}}));
}

TEST(nothing_and_one) {
    ASSERT_TRUE(merge_intervals({}).empty());
    ASSERT_TRUE((merge_intervals({{4, 4}}) == V{{4, 4}}));
}

TEST(duplicates) {
    ASSERT_TRUE((merge_intervals({{1, 2}, {1, 2}, {1, 2}}) == V{{1, 2}}));
}

TEST(same_start_different_ends) {
    ASSERT_TRUE((merge_intervals({{1, 2}, {1, 9}, {1, 4}}) == V{{1, 9}}));
}

TEST(negative_numbers) {
    ASSERT_TRUE((merge_intervals({{-5, -1}, {-2, 3}, {7, 8}}) == V{{-5, 3}, {7, 8}}));
}

TEST(many_intervals) {
    V in;
    for (int i = 999; i >= 0; i--) {
        in.push_back({i * 10, i * 10 + 5});
    }
    auto out = merge_intervals(in);
    ASSERT_EQ_INT(1000, (int)out.size());
    ASSERT_TRUE((out.front() == Interval{0, 5}));
    ASSERT_TRUE((out.back() == Interval{9990, 9995}));
}

CTEST_MAIN
