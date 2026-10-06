#include "ctest.h"
#include "bitset.h"

#include <string.h>

static BitSet with(const int *bits, int n) {
    BitSet s;
    bs_clear_all(&s);
    for (int i = 0; i < n; i++) {
        bs_set(&s, bits[i]);
    }
    return s;
}

TEST(clear_all_turns_everything_off) {
    BitSet s;
    memset(s.bytes, 0xFF, sizeof s.bytes);
    bs_clear_all(&s);
    ASSERT_EQ_INT(0, bs_count(&s));
    for (int i = 0; i < (int)sizeof s.bytes; i++) {
        ASSERT_EQ_INT(0, s.bytes[i]);
    }
}

TEST(set_and_test) {
    BitSet s;
    bs_clear_all(&s);
    ASSERT_EQ_INT(0, bs_test(&s, 5));
    ASSERT_EQ_INT(0, bs_set(&s, 5));
    ASSERT_EQ_INT(1, bs_test(&s, 5));
    ASSERT_EQ_INT(0, bs_test(&s, 4));
    ASSERT_EQ_INT(0, bs_test(&s, 6));
}

TEST(bits_live_where_the_layout_says) {
    BitSet s;
    bs_clear_all(&s);
    bs_set(&s, 0);
    ASSERT_EQ_INT(1, s.bytes[0]);
    bs_set(&s, 7);
    ASSERT_EQ_INT(129, s.bytes[0]);
    bs_set(&s, 8);
    ASSERT_EQ_INT(1, s.bytes[1]);
    bs_set(&s, 255);
    ASSERT_EQ_INT(128, s.bytes[31]);
}

TEST(setting_twice_is_the_same_as_once) {
    BitSet s;
    bs_clear_all(&s);
    bs_set(&s, 42);
    bs_set(&s, 42);
    ASSERT_EQ_INT(1, bs_count(&s));
}

TEST(clear_turns_one_bit_off) {
    int bits[] = {8, 9, 10};
    BitSet s = with(bits, 3);
    ASSERT_EQ_INT(0, bs_clear(&s, 9));
    ASSERT_EQ_INT(1, bs_test(&s, 8));
    ASSERT_EQ_INT(0, bs_test(&s, 9));
    ASSERT_EQ_INT(1, bs_test(&s, 10));
    ASSERT_EQ_INT(0, bs_clear(&s, 9));
    ASSERT_EQ_INT(2, bs_count(&s));
}

TEST(out_of_range_is_refused_and_changes_nothing) {
    BitSet s;
    bs_clear_all(&s);
    ASSERT_EQ_INT(-1, bs_set(&s, -1));
    ASSERT_EQ_INT(-1, bs_set(&s, 256));
    ASSERT_EQ_INT(-1, bs_set(&s, 100000));
    ASSERT_EQ_INT(-1, bs_clear(&s, 256));
    ASSERT_EQ_INT(-1, bs_test(&s, -1));
    ASSERT_EQ_INT(-1, bs_test(&s, 256));
    ASSERT_EQ_INT(0, bs_count(&s));
}

TEST(count) {
    int bits[] = {0, 1, 7, 8, 100, 255};
    BitSet s = with(bits, 6);
    ASSERT_EQ_INT(6, bs_count(&s));
    BitSet full;
    memset(full.bytes, 0xFF, sizeof full.bytes);
    ASSERT_EQ_INT(256, bs_count(&full));
}

TEST(next_finds_the_first_bit_at_or_after) {
    int bits[] = {3, 200};
    BitSet s = with(bits, 2);
    ASSERT_EQ_INT(3, bs_next(&s, 0));
    ASSERT_EQ_INT(3, bs_next(&s, 3));
    ASSERT_EQ_INT(200, bs_next(&s, 4));
    ASSERT_EQ_INT(200, bs_next(&s, 200));
    ASSERT_EQ_INT(-1, bs_next(&s, 201));
}

TEST(next_at_the_edges) {
    int bits[] = {0, 255};
    BitSet s = with(bits, 2);
    ASSERT_EQ_INT(0, bs_next(&s, -50));
    ASSERT_EQ_INT(255, bs_next(&s, 1));
    ASSERT_EQ_INT(-1, bs_next(&s, 256));
    ASSERT_EQ_INT(-1, bs_next(&s, 9999));
    BitSet empty;
    bs_clear_all(&empty);
    ASSERT_EQ_INT(-1, bs_next(&empty, 0));
}

TEST(next_walks_every_set_bit) {
    int bits[] = {2, 3, 64, 65, 190};
    BitSet s = with(bits, 5);
    int seen = 0;
    for (int n = bs_next(&s, 0); n >= 0; n = bs_next(&s, n + 1)) {
        ASSERT_EQ_INT(bits[seen], n);
        seen++;
    }
    ASSERT_EQ_INT(5, seen);
}

TEST(union_turns_on_what_either_has) {
    int a_bits[] = {1, 2, 3};
    int b_bits[] = {3, 4, 250};
    BitSet a = with(a_bits, 3);
    BitSet b = with(b_bits, 3);
    bs_union(&a, &b);
    ASSERT_EQ_INT(5, bs_count(&a));
    ASSERT_EQ_INT(1, bs_test(&a, 250));
    ASSERT_EQ_INT(1, bs_test(&a, 1));
    ASSERT_EQ_INT(3, bs_count(&b)); /* src untouched */
}

TEST(intersect_keeps_what_both_have) {
    int a_bits[] = {1, 2, 3, 99};
    int b_bits[] = {3, 4, 99};
    BitSet a = with(a_bits, 4);
    BitSet b = with(b_bits, 3);
    bs_intersect(&a, &b);
    ASSERT_EQ_INT(2, bs_count(&a));
    ASSERT_EQ_INT(1, bs_test(&a, 3));
    ASSERT_EQ_INT(1, bs_test(&a, 99));
    ASSERT_EQ_INT(0, bs_test(&a, 1));
    ASSERT_EQ_INT(3, bs_count(&b));
}

TEST(a_set_with_itself) {
    int bits[] = {10, 20};
    BitSet s = with(bits, 2);
    bs_union(&s, &s);
    ASSERT_EQ_INT(2, bs_count(&s));
    bs_intersect(&s, &s);
    ASSERT_EQ_INT(2, bs_count(&s));
}

CTEST_MAIN
