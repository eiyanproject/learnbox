#include "ctest.h"
#include "str.h"

#include <string.h>

TEST(length_does_not_count_the_terminator) {
    ASSERT_EQ_INT(3, my_strlen("ada"));
}

TEST(length_of_an_empty_string) {
    ASSERT_EQ_INT(0, my_strlen(""));
}

TEST(copy_into_a_large_enough_buffer) {
    char buf[16] = {0};
    ASSERT_EQ_INT(3, copy_into(buf, 16, "ada"));
    ASSERT_STR_EQ("ada", buf);
}

TEST(copy_truncates_rather_than_overflowing) {
    char buf[4];
    /* A guard byte after the buffer: if the copy writes past the end, this
       changes and the test fails rather than corrupting something silently. */
    char guard = '#';
    ASSERT_EQ_INT(3, copy_into(buf, 4, "abcdefgh"));
    ASSERT_STR_EQ("abc", buf);
    ASSERT_EQ_INT('#', guard);
}

TEST(copy_always_terminates) {
    char buf[4] = {'x', 'x', 'x', 'x'};
    copy_into(buf, 4, "abcdefgh");
    ASSERT_EQ_INT(0, buf[3]);
}

TEST(copy_with_no_room_at_all) {
    char buf[1] = {'z'};
    ASSERT_EQ_INT(0, copy_into(buf, 0, "abc"));
    ASSERT_EQ_INT('z', buf[0]); /* untouched */
}

TEST(copy_with_room_for_the_terminator_only) {
    char buf[1];
    ASSERT_EQ_INT(0, copy_into(buf, 1, "abc"));
    ASSERT_EQ_INT(0, buf[0]);
}

TEST(copy_an_empty_source) {
    char buf[8];
    ASSERT_EQ_INT(0, copy_into(buf, 8, ""));
    ASSERT_STR_EQ("", buf);
}

TEST(counts_occurrences) {
    ASSERT_EQ_INT(2, count_char("banana", 'n'));
    ASSERT_EQ_INT(3, count_char("banana", 'a'));
}

TEST(counts_none) {
    ASSERT_EQ_INT(0, count_char("banana", 'z'));
    ASSERT_EQ_INT(0, count_char("", 'a'));
}

TEST(reverses_in_place) {
    char buf[8];
    strcpy(buf, "abcd");
    reverse_in_place(buf);
    ASSERT_STR_EQ("dcba", buf);
}

TEST(reverses_an_odd_length_string) {
    char buf[8];
    strcpy(buf, "abc");
    reverse_in_place(buf);
    ASSERT_STR_EQ("cba", buf);
}

TEST(reversing_short_strings_is_safe) {
    char one[2] = "a";
    char none[1] = "";
    reverse_in_place(one);
    reverse_in_place(none);
    ASSERT_STR_EQ("a", one);
    ASSERT_STR_EQ("", none);
}

CTEST_MAIN
