#include "ctest.h"
#include "list.h"

TEST(a_new_list_is_empty) {
    struct List list;
    list_init(&list);
    ASSERT_NULL(list.head);
    ASSERT_EQ_INT(0, list.count);
}

TEST(push_front_prepends) {
    struct List list;
    list_init(&list);
    list_push_front(&list, 1);
    list_push_front(&list, 2);
    ASSERT_EQ_INT(2, list.head->value);
    ASSERT_EQ_INT(1, list.head->next->value);
    list_free(&list);
}

TEST(push_back_appends) {
    struct List list;
    list_init(&list);
    list_push_back(&list, 1);
    list_push_back(&list, 2);
    ASSERT_EQ_INT(1, list.head->value);
    ASSERT_EQ_INT(2, list.head->next->value);
    list_free(&list);
}

TEST(push_back_onto_an_empty_list_sets_the_head) {
    struct List list;
    list_init(&list);
    list_push_back(&list, 7);
    ASSERT_NOT_NULL(list.head);
    ASSERT_EQ_INT(7, list.head->value);
    list_free(&list);
}

TEST(the_count_tracks_the_contents) {
    struct List list;
    list_init(&list);
    list_push_front(&list, 1);
    list_push_back(&list, 2);
    ASSERT_EQ_INT(2, list.count);
    list_free(&list);
}

TEST(contains_finds_values) {
    struct List list;
    list_init(&list);
    list_push_back(&list, 1);
    list_push_back(&list, 2);
    ASSERT_TRUE(list_contains(&list, 2));
    ASSERT_FALSE(list_contains(&list, 99));
    list_free(&list);
}

TEST(remove_from_the_middle) {
    struct List list;
    list_init(&list);
    list_push_back(&list, 1);
    list_push_back(&list, 2);
    list_push_back(&list, 3);
    ASSERT_TRUE(list_remove(&list, 2));
    ASSERT_FALSE(list_contains(&list, 2));
    ASSERT_EQ_INT(2, list.count);
    list_free(&list);
}

TEST(remove_the_head) {
    /* The case the two-branch version gets wrong. */
    struct List list;
    list_init(&list);
    list_push_back(&list, 1);
    list_push_back(&list, 2);
    ASSERT_TRUE(list_remove(&list, 1));
    ASSERT_EQ_INT(2, list.head->value);
    ASSERT_EQ_INT(1, list.count);
    list_free(&list);
}

TEST(remove_the_only_element) {
    struct List list;
    list_init(&list);
    list_push_back(&list, 1);
    ASSERT_TRUE(list_remove(&list, 1));
    ASSERT_NULL(list.head);
    ASSERT_EQ_INT(0, list.count);
    list_free(&list);
}

TEST(remove_the_tail) {
    struct List list;
    list_init(&list);
    list_push_back(&list, 1);
    list_push_back(&list, 2);
    ASSERT_TRUE(list_remove(&list, 2));
    ASSERT_NULL(list.head->next);
    list_free(&list);
}

TEST(removing_something_absent_changes_nothing) {
    struct List list;
    list_init(&list);
    list_push_back(&list, 1);
    ASSERT_FALSE(list_remove(&list, 99));
    ASSERT_EQ_INT(1, list.count);
    list_free(&list);
}

TEST(free_empties_the_list) {
    struct List list;
    list_init(&list);
    for (int i = 0; i < 5; i++) {
        list_push_back(&list, i);
    }
    list_free(&list);
    ASSERT_NULL(list.head);
    ASSERT_EQ_INT(0, list.count);
}

CTEST_MAIN
