#include "ctest.h"
#include "vec.h"

#include <string.h>

TEST(a_new_vector_is_empty) {
    struct Vec v;
    ASSERT_TRUE(vec_init(&v, sizeof(int)));
    ASSERT_EQ_INT(0, (int)vec_count(&v));
    vec_free(&v);
}

TEST(init_rejects_a_zero_element_size) {
    struct Vec v;
    ASSERT_FALSE(vec_init(&v, 0));
}

TEST(push_then_get) {
    struct Vec v;
    vec_init(&v, sizeof(int));
    int value = 42;
    ASSERT_TRUE(vec_push(&v, &value));
    ASSERT_EQ_INT(42, *(int *)vec_get(&v, 0));
    vec_free(&v);
}

TEST(holds_many_elements_in_order) {
    struct Vec v;
    vec_init(&v, sizeof(int));
    for (int i = 0; i < 100; i++) {
        vec_push(&v, &i);
    }
    ASSERT_EQ_INT(100, (int)vec_count(&v));
    ASSERT_EQ_INT(0, *(int *)vec_get(&v, 0));
    ASSERT_EQ_INT(99, *(int *)vec_get(&v, 99));
    vec_free(&v);
}

TEST(capacity_grows_multiplicatively) {
    /* Doubling means the capacity outruns the count, and n appends stay
       amortised constant rather than quadratic. */
    struct Vec v;
    vec_init(&v, sizeof(int));
    for (int i = 0; i < 100; i++) {
        vec_push(&v, &i);
    }
    ASSERT_TRUE(v.capacity >= 100);
    ASSERT_TRUE(v.capacity <= 256);
    vec_free(&v);
}

TEST(get_out_of_range_is_null) {
    struct Vec v;
    vec_init(&v, sizeof(int));
    int value = 1;
    vec_push(&v, &value);
    ASSERT_NULL(vec_get(&v, 1));
    ASSERT_NULL(vec_get(&v, 99));
    vec_free(&v);
}

TEST(pop_returns_the_last_element) {
    struct Vec v;
    vec_init(&v, sizeof(int));
    for (int i = 1; i <= 3; i++) {
        vec_push(&v, &i);
    }
    int out = 0;
    ASSERT_TRUE(vec_pop(&v, &out));
    ASSERT_EQ_INT(3, out);
    ASSERT_EQ_INT(2, (int)vec_count(&v));
    vec_free(&v);
}

TEST(pop_from_empty_fails) {
    struct Vec v;
    vec_init(&v, sizeof(int));
    int out = 99;
    ASSERT_FALSE(vec_pop(&v, &out));
    ASSERT_EQ_INT(99, out);
    vec_free(&v);
}

TEST(pop_accepts_a_null_destination) {
    struct Vec v;
    vec_init(&v, sizeof(int));
    int value = 1;
    vec_push(&v, &value);
    ASSERT_TRUE(vec_pop(&v, NULL));
    ASSERT_EQ_INT(0, (int)vec_count(&v));
    vec_free(&v);
}

TEST(the_same_vector_holds_structs) {
    /* The point of the element size: one implementation, any type. */
    struct Point { int x, y; };
    struct Vec v;
    vec_init(&v, sizeof(struct Point));
    struct Point p = {3, 4};
    vec_push(&v, &p);
    struct Point *got = vec_get(&v, 0);
    ASSERT_EQ_INT(3, got->x);
    ASSERT_EQ_INT(4, got->y);
    vec_free(&v);
}

TEST(it_holds_strings_by_pointer) {
    struct Vec v;
    vec_init(&v, sizeof(const char *));
    const char *name = "ada";
    vec_push(&v, &name);
    ASSERT_STR_EQ("ada", *(const char **)vec_get(&v, 0));
    vec_free(&v);
}

TEST(free_resets_the_vector) {
    struct Vec v;
    vec_init(&v, sizeof(int));
    int value = 1;
    vec_push(&v, &value);
    vec_free(&v);
    ASSERT_EQ_INT(0, (int)vec_count(&v));
    ASSERT_NULL(v.data);
}

CTEST_MAIN
