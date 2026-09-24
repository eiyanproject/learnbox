#include "ctest.h"
#include "io.h"

#include <stdio.h>
#include <string.h>

static const char *PATH = "learnbox_io_test.txt";
static const char *UNOPENABLE = "/nonexistent-directory-xyz/file.txt";

TEST(write_then_count) {
    const char *lines[] = {"one", "two", "three"};
    ASSERT_EQ_INT(3, write_lines(PATH, lines, 3));
    ASSERT_EQ_INT(3, count_lines(PATH));
    remove(PATH);
}

TEST(write_zero_lines) {
    const char *lines[] = {"unused"};
    ASSERT_EQ_INT(0, write_lines(PATH, lines, 0));
    ASSERT_EQ_INT(0, count_lines(PATH));
    remove(PATH);
}

TEST(write_truncates_an_existing_file) {
    const char *many[] = {"a", "b", "c"};
    const char *one[] = {"z"};
    write_lines(PATH, many, 3);
    write_lines(PATH, one, 1);
    ASSERT_EQ_INT(1, count_lines(PATH));
    remove(PATH);
}

TEST(write_reports_failure_rather_than_crashing) {
    const char *lines[] = {"x"};
    ASSERT_EQ_INT(-1, write_lines(UNOPENABLE, lines, 1));
}

TEST(a_final_line_without_a_newline_still_counts) {
    FILE *f = fopen(PATH, "w");
    fputs("one\ntwo", f); /* no trailing newline */
    fclose(f);
    ASSERT_EQ_INT(2, count_lines(PATH));
    remove(PATH);
}

TEST(count_reports_failure_for_a_missing_file) {
    ASSERT_EQ_INT(-1, count_lines("definitely-not-here.txt"));
}

TEST(read_first_line_strips_the_newline) {
    const char *lines[] = {"hello", "world"};
    write_lines(PATH, lines, 2);
    char buf[64];
    ASSERT_EQ_INT(5, read_first_line(PATH, buf, sizeof buf));
    ASSERT_STR_EQ("hello", buf);
    remove(PATH);
}

TEST(read_first_line_respects_the_buffer_size) {
    const char *lines[] = {"abcdefghij"};
    write_lines(PATH, lines, 1);
    char buf[4];
    int n = read_first_line(PATH, buf, sizeof buf);
    ASSERT_EQ_INT(3, n);
    ASSERT_STR_EQ("abc", buf);
    remove(PATH);
}

TEST(read_first_line_of_a_missing_file) {
    char buf[16];
    ASSERT_EQ_INT(-1, read_first_line("definitely-not-here.txt", buf, sizeof buf));
}

TEST(append_adds_without_truncating) {
    const char *lines[] = {"one"};
    write_lines(PATH, lines, 1);
    ASSERT_EQ_INT(0, append_line(PATH, "two"));
    ASSERT_EQ_INT(2, count_lines(PATH));
    remove(PATH);
}

TEST(append_creates_the_file_if_missing) {
    remove(PATH);
    ASSERT_EQ_INT(0, append_line(PATH, "first"));
    ASSERT_EQ_INT(1, count_lines(PATH));
    remove(PATH);
}

TEST(append_reports_failure) {
    ASSERT_EQ_INT(-1, append_line(UNOPENABLE, "x"));
}

CTEST_MAIN
