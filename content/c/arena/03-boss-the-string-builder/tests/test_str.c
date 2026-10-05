#include "ctest.h"
#include "str.h"

#include <string.h>

/* The three promises, checked after every step that matters. */
#define ASSERT_SOUND(s)                         \
    do {                                        \
        ASSERT_NOT_NULL((s).data);              \
        ASSERT_TRUE((s).cap > (s).len);         \
        ASSERT_EQ_INT(0, (s).data[(s).len]);    \
        ASSERT_EQ_INT((int)(s).len, (int)strlen((s).data)); \
    } while (0)

TEST(init_makes_an_empty_string) {
    Str s = {0};
    ASSERT_EQ_INT(0, str_init(&s));
    ASSERT_SOUND(s);
    ASSERT_EQ_INT(0, (int)s.len);
    ASSERT_STR_EQ("", s.data);
    str_free(&s);
}

TEST(append) {
    Str s = {0};
    str_init(&s);
    ASSERT_EQ_INT(0, str_append(&s, "hello"));
    ASSERT_EQ_INT(0, str_append(&s, ", "));
    ASSERT_EQ_INT(0, str_append(&s, "world"));
    ASSERT_SOUND(s);
    ASSERT_STR_EQ("hello, world", s.data);
    ASSERT_EQ_INT(12, (int)s.len);
    str_free(&s);
}

TEST(append_nothing) {
    Str s = {0};
    str_init(&s);
    str_append(&s, "abc");
    ASSERT_EQ_INT(0, str_append(&s, ""));
    ASSERT_SOUND(s);
    ASSERT_STR_EQ("abc", s.data);
    str_free(&s);
}

TEST(append_char) {
    Str s = {0};
    str_init(&s);
    for (char c = 'a'; c <= 'e'; c++) {
        ASSERT_EQ_INT(0, str_append_char(&s, c));
    }
    ASSERT_SOUND(s);
    ASSERT_STR_EQ("abcde", s.data);
    str_free(&s);
}

TEST(it_grows_past_any_first_buffer) {
    Str s = {0};
    str_init(&s);
    for (int i = 0; i < 3000; i++) {
        ASSERT_EQ_INT(0, str_append(&s, "ab"));
    }
    ASSERT_SOUND(s);
    ASSERT_EQ_INT(6000, (int)s.len);
    ASSERT_EQ_INT('a', s.data[0]);
    ASSERT_EQ_INT('b', s.data[5999]);
    ASSERT_EQ_INT('a', s.data[2998]);
    str_free(&s);
}

TEST(one_long_append) {
    char big[5001];
    memset(big, 'x', 5000);
    big[5000] = 0;
    Str s = {0};
    str_init(&s);
    str_append(&s, "[");
    ASSERT_EQ_INT(0, str_append(&s, big));
    str_append(&s, "]");
    ASSERT_SOUND(s);
    ASSERT_EQ_INT(5002, (int)s.len);
    ASSERT_EQ_INT('[', s.data[0]);
    ASSERT_EQ_INT(']', s.data[5001]);
    str_free(&s);
}

TEST(insert_at_the_front_middle_and_end) {
    Str s = {0};
    str_init(&s);
    str_append(&s, "world");
    ASSERT_EQ_INT(0, str_insert(&s, 0, "hello "));
    ASSERT_STR_EQ("hello world", s.data);
    ASSERT_EQ_INT(0, str_insert(&s, 5, ","));
    ASSERT_STR_EQ("hello, world", s.data);
    ASSERT_EQ_INT(0, str_insert(&s, s.len, "!"));
    ASSERT_STR_EQ("hello, world!", s.data);
    ASSERT_SOUND(s);
    str_free(&s);
}

TEST(insert_past_the_end_is_refused) {
    Str s = {0};
    str_init(&s);
    str_append(&s, "abc");
    ASSERT_EQ_INT(-1, str_insert(&s, 4, "x"));
    ASSERT_EQ_INT(-1, str_insert(&s, 1000, "x"));
    ASSERT_STR_EQ("abc", s.data);
    ASSERT_EQ_INT(3, (int)s.len);
    ASSERT_SOUND(s);
    str_free(&s);
}

TEST(insert_that_has_to_grow) {
    char big[2001];
    memset(big, 'y', 2000);
    big[2000] = 0;
    Str s = {0};
    str_init(&s);
    str_append(&s, "<>");
    ASSERT_EQ_INT(0, str_insert(&s, 1, big));
    ASSERT_SOUND(s);
    ASSERT_EQ_INT(2002, (int)s.len);
    ASSERT_EQ_INT('<', s.data[0]);
    ASSERT_EQ_INT('y', s.data[1]);
    ASSERT_EQ_INT('y', s.data[2000]);
    ASSERT_EQ_INT('>', s.data[2001]);
    str_free(&s);
}

TEST(clear_empties_and_keeps_the_buffer) {
    Str s = {0};
    str_init(&s);
    for (int i = 0; i < 100; i++) {
        str_append(&s, "0123456789");
    }
    size_t cap = s.cap;
    str_clear(&s);
    ASSERT_SOUND(s);
    ASSERT_EQ_INT(0, (int)s.len);
    ASSERT_STR_EQ("", s.data);
    ASSERT_TRUE(s.cap == cap);
    ASSERT_EQ_INT(0, str_append(&s, "again"));
    ASSERT_STR_EQ("again", s.data);
    str_free(&s);
}

TEST(free_resets_and_is_safe_twice) {
    Str s = {0};
    str_init(&s);
    str_append(&s, "abc");
    str_free(&s);
    ASSERT_NULL(s.data);
    ASSERT_EQ_INT(0, (int)s.len);
    ASSERT_EQ_INT(0, (int)s.cap);
    str_free(&s);
    ASSERT_NULL(s.data);
}

TEST(two_strings_do_not_share) {
    Str a = {0};
    Str b = {0};
    str_init(&a);
    str_init(&b);
    str_append(&a, "left");
    str_append(&b, "right");
    ASSERT_TRUE(a.data != b.data);
    ASSERT_STR_EQ("left", a.data);
    ASSERT_STR_EQ("right", b.data);
    str_free(&a);
    str_free(&b);
}

CTEST_MAIN
