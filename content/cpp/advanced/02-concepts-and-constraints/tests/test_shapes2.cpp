#include "ctest.h"
#include "shapes2.h"

#include <string>
#include <vector>

struct Tag {
    std::string name() const { return "tag"; }
};

struct Anonymous {
    int value = 1;
};

TEST(numeric_accepts_integers_and_floats) {
    static_assert(Numeric<int>);
    static_assert(Numeric<long>);
    static_assert(Numeric<double>);
    ASSERT_TRUE(true);
}

TEST(numeric_rejects_other_types) {
    static_assert(!Numeric<std::string>);
    static_assert(!Numeric<Tag>);
    ASSERT_TRUE(true);
}

TEST(named_accepts_a_type_with_name) {
    static_assert(Named<Tag>);
    ASSERT_TRUE(true);
}

TEST(named_rejects_a_type_without_name) {
    static_assert(!Named<Anonymous>);
    static_assert(!Named<int>);
    ASSERT_TRUE(true);
}

TEST(sum_of_ints) {
    std::vector<int> v = {1, 2, 3};
    ASSERT_EQ_INT(6, sum(v));
}

TEST(sum_of_doubles) {
    std::vector<double> v = {0.5, 0.25};
    ASSERT_NEAR(0.75, sum(v), 1e-9);
}

TEST(sum_of_nothing_is_the_value_initialised_zero) {
    std::vector<int> v;
    ASSERT_EQ_INT(0, sum(v));
}

TEST(label_uses_the_name) {
    ASSERT_STR_EQ("[tag]", label(Tag{}).c_str());
}

TEST(describe_takes_the_numeric_branch) {
    ASSERT_STR_EQ("number 42", describe(42).c_str());
}

TEST(describe_takes_the_named_branch) {
    /* value.name() would be a hard error for int - it compiles only because
       the untaken if constexpr branch is discarded. */
    ASSERT_STR_EQ("named tag", describe(Tag{}).c_str());
}

TEST(describe_falls_through_for_anything_else) {
    ASSERT_STR_EQ("unknown", describe(Anonymous{}).c_str());
}

TEST(clamp_to_pins_both_ends) {
    ASSERT_EQ_INT(0, clamp_to(-5, 0, 10));
    ASSERT_EQ_INT(10, clamp_to(50, 0, 10));
    ASSERT_EQ_INT(7, clamp_to(7, 0, 10));
}

TEST(clamp_to_works_on_doubles_too) {
    ASSERT_NEAR(1.0, clamp_to(2.5, 0.0, 1.0), 1e-9);
}

CTEST_MAIN
