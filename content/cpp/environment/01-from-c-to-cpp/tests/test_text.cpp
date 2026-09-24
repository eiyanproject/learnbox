#include "ctest.h"
#include "text.h"

TEST(join_with_a_separator) {
    ASSERT_STR_EQ("a,b,c", join({"a", "b", "c"}, ",").c_str());
}

TEST(join_of_one_has_no_separator) {
    ASSERT_STR_EQ("a", join({"a"}, ",").c_str());
}

TEST(join_of_nothing_is_empty) {
    ASSERT_STR_EQ("", join({}, ",").c_str());
}

TEST(join_with_a_longer_separator) {
    ASSERT_STR_EQ("a -> b", join({"a", "b"}, " -> ").c_str());
}

TEST(counts_words) {
    ASSERT_EQ_INT(3, word_count("the cat sat"));
}

TEST(word_count_ignores_extra_whitespace) {
    ASSERT_EQ_INT(2, word_count("  a   b  "));
}

TEST(word_count_of_empty) {
    ASSERT_EQ_INT(0, word_count(""));
    ASSERT_EQ_INT(0, word_count("   "));
}

TEST(to_upper_uppercases) {
    ASSERT_STR_EQ("HELLO", to_upper("hello").c_str());
}

TEST(to_upper_leaves_the_original_alone) {
    std::string original = "hello";
    to_upper(original);
    ASSERT_STR_EQ("hello", original.c_str());
}

TEST(longest_finds_it) {
    ASSERT_STR_EQ("grace", longest({"ada", "grace", "bob"}).c_str());
}

TEST(longest_returns_the_first_on_a_tie) {
    ASSERT_STR_EQ("ada", longest({"ada", "bob"}).c_str());
}

TEST(longest_of_empty) {
    ASSERT_STR_EQ("", longest({}).c_str());
}

CTEST_MAIN
