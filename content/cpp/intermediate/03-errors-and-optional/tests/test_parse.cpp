#include "ctest.h"
#include "parse.h"

#include <stdexcept>
#include <string>
#include <vector>

TEST(parses_a_number) {
    auto n = parse_int("123");
    ASSERT_TRUE(n.has_value());
    ASSERT_EQ_INT(123, *n);
}

TEST(parses_a_negative_number) {
    ASSERT_EQ_INT(-42, *parse_int("-42"));
}

TEST(rejects_letters) {
    ASSERT_FALSE(parse_int("12a").has_value());
    ASSERT_FALSE(parse_int("abc").has_value());
}

TEST(rejects_an_empty_string_and_a_bare_minus) {
    ASSERT_FALSE(parse_int("").has_value());
    ASSERT_FALSE(parse_int("-").has_value());
}

TEST(divide_works) {
    ASSERT_EQ_INT(3, divide(7, 2));
}

TEST(divide_by_zero_throws_domain_error) {
    bool threw = false;
    try {
        divide(1, 0);
    } catch (const std::domain_error&) {
        threw = true;
    }
    ASSERT_TRUE(threw);
}

TEST(parse_all_keeps_the_good_ones) {
    std::vector<std::string> items = {"1", "two", "3"};
    int failed = 0;
    auto out = parse_all(items, &failed);
    ASSERT_EQ_INT(2, (int)out.size());
    ASSERT_EQ_INT(1, out[0]);
    ASSERT_EQ_INT(3, out[1]);
}

TEST(parse_all_counts_the_failures) {
    std::vector<std::string> items = {"1", "two", "three"};
    int failed = 0;
    parse_all(items, &failed);
    ASSERT_EQ_INT(2, failed);
}

TEST(parse_all_accepts_a_null_out_parameter) {
    std::vector<std::string> items = {"1"};
    auto out = parse_all(items, nullptr);
    ASSERT_EQ_INT(1, (int)out.size());
}

TEST(parse_all_of_nothing) {
    std::vector<std::string> items;
    int failed = 99;
    auto out = parse_all(items, &failed);
    ASSERT_TRUE(out.empty());
    ASSERT_EQ_INT(0, failed);
}

TEST(parse_or_falls_back) {
    ASSERT_EQ_INT(7, parse_or("junk", 7));
    ASSERT_EQ_INT(12, parse_or("12", 7));
}

TEST(zero_parses_as_a_value_not_as_absence) {
    /* An optional distinguishes "the value is 0" from "there is no value",
       which a -1 or 0 sentinel cannot. */
    auto n = parse_int("0");
    ASSERT_TRUE(n.has_value());
    ASSERT_EQ_INT(0, *n);
}

CTEST_MAIN
