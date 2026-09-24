#include "ctest.h"
#include "shape.h"

TEST(point_of_sets_both_fields) {
    struct Point p = point_of(3, 4);
    ASSERT_EQ_INT(3, p.x);
    ASSERT_EQ_INT(4, p.y);
}

TEST(move_point_changes_the_caller) {
    struct Point p = point_of(1, 1);
    move_point(&p, 2, 3);
    ASSERT_EQ_INT(3, p.x);
    ASSERT_EQ_INT(4, p.y);
}

TEST(move_point_accepts_negative_deltas) {
    struct Point p = point_of(5, 5);
    move_point(&p, -2, -10);
    ASSERT_EQ_INT(3, p.x);
    ASSERT_EQ_INT(-5, p.y);
}

TEST(rect_area) {
    struct Rect r = {{0, 0}, 3, 4};
    ASSERT_EQ_INT(12, rect_area(&r));
}

TEST(rect_area_of_a_flat_rect) {
    struct Rect r = {{0, 0}, 5, 0};
    ASSERT_EQ_INT(0, rect_area(&r));
}

TEST(contains_a_point_inside) {
    struct Rect r = {{0, 0}, 4, 4};
    ASSERT_TRUE(rect_contains(&r, point_of(2, 2)));
}

TEST(the_origin_is_inside) {
    struct Rect r = {{1, 1}, 4, 4};
    ASSERT_TRUE(rect_contains(&r, point_of(1, 1)));
}

TEST(the_far_edge_is_outside) {
    struct Rect r = {{0, 0}, 4, 4};
    ASSERT_FALSE(rect_contains(&r, point_of(4, 2)));
    ASSERT_FALSE(rect_contains(&r, point_of(2, 4)));
}

TEST(points_before_the_origin_are_outside) {
    struct Rect r = {{2, 2}, 4, 4};
    ASSERT_FALSE(rect_contains(&r, point_of(1, 3)));
}

TEST(grow_returns_a_bigger_rect) {
    struct Rect r = {{1, 2}, 3, 4};
    struct Rect bigger = rect_grow(r, 2);
    ASSERT_EQ_INT(5, bigger.w);
    ASSERT_EQ_INT(6, bigger.h);
}

TEST(grow_keeps_the_origin) {
    struct Rect r = {{1, 2}, 3, 4};
    struct Rect bigger = rect_grow(r, 2);
    ASSERT_EQ_INT(1, bigger.origin.x);
    ASSERT_EQ_INT(2, bigger.origin.y);
}

TEST(grow_leaves_the_original_alone) {
    /* The struct was passed by value, so the caller's copy is untouched. */
    struct Rect r = {{1, 2}, 3, 4};
    rect_grow(r, 10);
    ASSERT_EQ_INT(3, r.w);
}

CTEST_MAIN
