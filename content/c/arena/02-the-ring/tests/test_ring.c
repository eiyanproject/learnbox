#include "ctest.h"
#include "ring.h"

static Ring filled(int n) {
    Ring r;
    ring_init(&r);
    for (int i = 1; i <= n; i++) {
        ring_push(&r, i);
    }
    return r;
}

TEST(starts_empty) {
    Ring r;
    r.head = 3;
    r.count = 2;
    ring_init(&r);
    ASSERT_EQ_INT(0, ring_count(&r));
}

TEST(push_reports_room) {
    Ring r;
    ring_init(&r);
    for (int i = 1; i <= RING_CAP; i++) {
        ASSERT_EQ_INT(1, ring_push(&r, i));
        ASSERT_EQ_INT(i, ring_count(&r));
    }
}

TEST(pop_gives_the_oldest_first) {
    Ring r = filled(3);
    int v = 0;
    ASSERT_EQ_INT(1, ring_pop(&r, &v));
    ASSERT_EQ_INT(1, v);
    ASSERT_EQ_INT(1, ring_pop(&r, &v));
    ASSERT_EQ_INT(2, v);
    ASSERT_EQ_INT(1, ring_count(&r));
}

TEST(pop_on_empty_leaves_out_alone) {
    Ring r;
    ring_init(&r);
    int v = 77;
    ASSERT_EQ_INT(0, ring_pop(&r, &v));
    ASSERT_EQ_INT(77, v);
    ASSERT_EQ_INT(0, ring_count(&r));
}

TEST(a_full_ring_overwrites_the_oldest) {
    Ring r = filled(4);
    int v = 0;
    ASSERT_EQ_INT(0, ring_push(&r, 5));
    ASSERT_EQ_INT(RING_CAP, ring_count(&r));
    ASSERT_EQ_INT(1, ring_pop(&r, &v));
    ASSERT_EQ_INT(2, v);
}

TEST(overwriting_many_times_keeps_the_newest_four) {
    Ring r = filled(11);
    int v = 0;
    for (int want = 8; want <= 11; want++) {
        ASSERT_EQ_INT(1, ring_pop(&r, &v));
        ASSERT_EQ_INT(want, v);
    }
    ASSERT_EQ_INT(0, ring_pop(&r, &v));
}

TEST(peek_reads_without_removing) {
    Ring r = filled(3);
    int v = 0;
    ASSERT_EQ_INT(1, ring_peek(&r, 0, &v));
    ASSERT_EQ_INT(1, v);
    ASSERT_EQ_INT(1, ring_peek(&r, 2, &v));
    ASSERT_EQ_INT(3, v);
    ASSERT_EQ_INT(3, ring_count(&r));
}

TEST(peek_out_of_range) {
    Ring r = filled(2);
    int v = 77;
    ASSERT_EQ_INT(0, ring_peek(&r, 2, &v));
    ASSERT_EQ_INT(0, ring_peek(&r, -1, &v));
    ASSERT_EQ_INT(0, ring_peek(&r, RING_CAP, &v));
    ASSERT_EQ_INT(77, v);
}

TEST(peek_follows_the_wrap) {
    Ring r = filled(6); /* holds 3 4 5 6 */
    int v = 0;
    for (int i = 0; i < RING_CAP; i++) {
        ASSERT_EQ_INT(1, ring_peek(&r, i, &v));
        ASSERT_EQ_INT(3 + i, v);
    }
}

TEST(push_and_pop_interleaved_wrap_around) {
    Ring r;
    ring_init(&r);
    int v = 0;
    for (int i = 1; i <= 20; i++) {
        ASSERT_EQ_INT(1, ring_push(&r, i));
        ASSERT_EQ_INT(1, ring_push(&r, i * 100));
        ASSERT_EQ_INT(1, ring_pop(&r, &v));
        ASSERT_EQ_INT(i, v);
        ASSERT_EQ_INT(1, ring_pop(&r, &v));
        ASSERT_EQ_INT(i * 100, v);
        ASSERT_EQ_INT(0, ring_count(&r));
    }
}

CTEST_MAIN
