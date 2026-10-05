#include "ctest.h"
#include "words.h"

#include <string.h>

TEST(counts_words) {
    ASSERT_EQ_INT(4, count_words("to be or not"));
    ASSERT_EQ_INT(1, count_words("one"));
}

TEST(extra_whitespace_does_not_make_words) {
    ASSERT_EQ_INT(2, count_words("  two   words\n"));
    ASSERT_EQ_INT(3, count_words("a\tb\nc"));
}

TEST(no_words) {
    ASSERT_EQ_INT(0, count_words(""));
    ASSERT_EQ_INT(0, count_words("   "));
    ASSERT_EQ_INT(0, count_words("\n\t "));
}

TEST(punctuation_is_part_of_a_word) {
    ASSERT_EQ_INT(2, count_words("hello, world!"));
}

TEST(trim_both_ends) {
    char s[] = "  hello world \n";
    ASSERT_EQ_INT(11, trim(s));
    ASSERT_STR_EQ("hello world", s);
}

TEST(trim_nothing_to_do) {
    char s[] = "tidy";
    ASSERT_EQ_INT(4, trim(s));
    ASSERT_STR_EQ("tidy", s);
}

TEST(trim_all_whitespace) {
    char s[] = "   ";
    ASSERT_EQ_INT(0, trim(s));
    ASSERT_STR_EQ("", s);
}

TEST(trim_empty) {
    char s[] = "";
    ASSERT_EQ_INT(0, trim(s));
    ASSERT_STR_EQ("", s);
}

TEST(trim_one_side_only) {
    char a[] = "\t\tleft";
    char b[] = "right  ";
    ASSERT_EQ_INT(4, trim(a));
    ASSERT_STR_EQ("left", a);
    ASSERT_EQ_INT(5, trim(b));
    ASSERT_STR_EQ("right", b);
}

TEST(trim_keeps_the_inside) {
    char s[] = " a  b ";
    ASSERT_EQ_INT(4, trim(s));
    ASSERT_STR_EQ("a  b", s);
}

TEST(trim_then_count) {
    char s[] = "   three little words  ";
    trim(s);
    ASSERT_EQ_INT(3, count_words(s));
    ASSERT_EQ_INT(18, (int)strlen(s));
}

CTEST_MAIN
