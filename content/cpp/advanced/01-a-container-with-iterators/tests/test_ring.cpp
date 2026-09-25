#include "ctest.h"
#include "ring.h"

#include <algorithm>
#include <iterator>
#include <numeric>
#include <string>
#include <type_traits>

TEST(a_new_ring_is_empty) {
    Ring<int, 4> r;
    ASSERT_TRUE(r.empty());
    ASSERT_FALSE(r.full());
    ASSERT_EQ_INT(0, (int)r.size());
    ASSERT_EQ_INT(4, (int)r.capacity());
}

TEST(pushing_grows_it) {
    Ring<int, 4> r;
    r.push(1);
    r.push(2);
    ASSERT_EQ_INT(2, (int)r.size());
    ASSERT_EQ_INT(1, r.front());
    ASSERT_EQ_INT(2, r.back());
}

TEST(it_reports_full_at_capacity) {
    Ring<int, 2> r;
    r.push(1);
    r.push(2);
    ASSERT_TRUE(r.full());
    ASSERT_EQ_INT(2, (int)r.size());
}

TEST(pushing_past_capacity_drops_the_oldest) {
    Ring<int, 3> r;
    r.push(1);
    r.push(2);
    r.push(3);
    r.push(4);
    ASSERT_EQ_INT(3, (int)r.size());
    ASSERT_EQ_INT(2, r.front());
    ASSERT_EQ_INT(4, r.back());
}

TEST(indexing_is_oldest_first_across_the_wrap) {
    Ring<int, 3> r;
    for (int n = 1; n <= 5; ++n) {
        r.push(n);
    }
    ASSERT_EQ_INT(3, r[0]);
    ASSERT_EQ_INT(4, r[1]);
    ASSERT_EQ_INT(5, r[2]);
}

TEST(elements_can_be_modified_through_the_index) {
    Ring<int, 3> r;
    r.push(1);
    r[0] = 99;
    ASSERT_EQ_INT(99, r.front());
}

TEST(range_for_visits_everything_in_order) {
    Ring<int, 3> r;
    for (int n = 1; n <= 5; ++n) {
        r.push(n);
    }
    std::string seen;
    for (int n : r) {
        seen += std::to_string(n);
    }
    ASSERT_STR_EQ("345", seen.c_str());
}

TEST(range_for_over_an_empty_ring_does_nothing) {
    Ring<int, 3> r;
    int visits = 0;
    for (int n : r) {
        (void)n;
        ++visits;
    }
    ASSERT_EQ_INT(0, visits);
}

TEST(the_iterator_has_the_traits_the_algorithms_need) {
    using It = Ring<int, 4>::const_iterator;
    static_assert(std::is_same_v<std::iterator_traits<It>::value_type, int>);
    static_assert(std::is_same_v<std::iterator_traits<It>::iterator_category,
                                 std::forward_iterator_tag>);
    ASSERT_TRUE(true);
}

TEST(std_find_works_on_it) {
    Ring<int, 4> r;
    r.push(10);
    r.push(20);
    r.push(30);
    auto it = std::find(r.begin(), r.end(), 20);
    ASSERT_TRUE(it != r.end());
    ASSERT_EQ_INT(20, *it);
}

TEST(std_find_reports_a_miss_as_end) {
    Ring<int, 4> r;
    r.push(10);
    ASSERT_TRUE(std::find(r.begin(), r.end(), 99) == r.end());
}

TEST(accumulate_works_on_it) {
    Ring<int, 4> r;
    for (int n = 1; n <= 6; ++n) {
        r.push(n);
    }
    /* 3 + 4 + 5 + 6 - the first two were overwritten. */
    ASSERT_EQ_INT(18, std::accumulate(r.begin(), r.end(), 0));
}

TEST(the_postfix_increment_returns_the_old_position) {
    Ring<int, 4> r;
    r.push(7);
    r.push(8);
    auto it = r.begin();
    auto before = it++;
    ASSERT_EQ_INT(7, *before);
    ASSERT_EQ_INT(8, *it);
}

TEST(it_holds_a_non_trivial_type) {
    Ring<std::string, 2> r;
    r.push("a");
    r.push("b");
    r.push("c");
    ASSERT_STR_EQ("b", r.front().c_str());
    ASSERT_STR_EQ("c", r.back().c_str());
}

CTEST_MAIN
