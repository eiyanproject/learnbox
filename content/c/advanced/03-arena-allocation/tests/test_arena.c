#include "ctest.h"
#include "arena.h"

#include <stdalign.h>
#include <stddef.h>
#include <string.h>

TEST(a_new_arena_has_used_nothing) {
    struct Arena a;
    ASSERT_TRUE(arena_init(&a, 1024));
    ASSERT_EQ_INT(0, (int)arena_used(&a));
    arena_free(&a);
}

TEST(init_rejects_a_zero_capacity) {
    struct Arena a;
    ASSERT_FALSE(arena_init(&a, 0));
}

TEST(alloc_returns_usable_memory) {
    struct Arena a;
    arena_init(&a, 1024);
    int *p = arena_alloc(&a, sizeof(int));
    ASSERT_NOT_NULL(p);
    *p = 42;
    ASSERT_EQ_INT(42, *p);
    arena_free(&a);
}

TEST(allocations_do_not_overlap) {
    struct Arena a;
    arena_init(&a, 1024);
    int *first = arena_alloc(&a, sizeof(int));
    int *second = arena_alloc(&a, sizeof(int));
    *first = 1;
    *second = 2;
    ASSERT_EQ_INT(1, *first);
    ASSERT_EQ_INT(2, *second);
    arena_free(&a);
}

TEST(allocations_are_aligned) {
    struct Arena a;
    arena_init(&a, 1024);
    arena_alloc(&a, 1); /* an odd size, to misalign the offset */
    void *p = arena_alloc(&a, sizeof(double));
    ASSERT_NOT_NULL(p);
    ASSERT_EQ_INT(0, (int)((size_t)p % alignof(max_align_t)));
    arena_free(&a);
}

TEST(used_grows_with_allocation) {
    struct Arena a;
    arena_init(&a, 1024);
    arena_alloc(&a, 100);
    ASSERT_TRUE(arena_used(&a) >= 100);
    arena_free(&a);
}

TEST(alloc_fails_when_it_does_not_fit) {
    struct Arena a;
    arena_init(&a, 64);
    ASSERT_NULL(arena_alloc(&a, 1000));
    arena_free(&a);
}

TEST(alloc_fails_gracefully_once_full) {
    struct Arena a;
    arena_init(&a, 64);
    while (arena_alloc(&a, 8) != NULL) {
        /* fill it */
    }
    ASSERT_NULL(arena_alloc(&a, 8));
    arena_free(&a);
}

TEST(a_huge_size_does_not_overflow_the_check) {
    struct Arena a;
    arena_init(&a, 64);
    ASSERT_NULL(arena_alloc(&a, (size_t)-1));
    arena_free(&a);
}

TEST(strdup_copies_into_the_arena) {
    struct Arena a;
    arena_init(&a, 1024);
    char *copy = arena_strdup(&a, "ada");
    ASSERT_NOT_NULL(copy);
    ASSERT_STR_EQ("ada", copy);
    arena_free(&a);
}

TEST(reset_reclaims_everything_at_once) {
    struct Arena a;
    arena_init(&a, 1024);
    arena_alloc(&a, 500);
    arena_reset(&a);
    ASSERT_EQ_INT(0, (int)arena_used(&a));
    /* And the space is available again. */
    ASSERT_NOT_NULL(arena_alloc(&a, 500));
    arena_free(&a);
}

TEST(the_arena_can_be_reused_many_times) {
    struct Arena a;
    arena_init(&a, 128);
    for (int i = 0; i < 100; i++) {
        char *s = arena_strdup(&a, "reused");
        ASSERT_NOT_NULL(s);
        arena_reset(&a);
    }
    arena_free(&a);
}

CTEST_MAIN
