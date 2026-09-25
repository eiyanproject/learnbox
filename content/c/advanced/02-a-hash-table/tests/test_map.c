#include "ctest.h"
#include "map.h"

#include <string.h>

TEST(the_hash_is_deterministic) {
    ASSERT_EQ_INT((int)hash_string("ada"), (int)hash_string("ada"));
}

TEST(different_keys_usually_hash_differently) {
    ASSERT_TRUE(hash_string("ada") != hash_string("grace"));
}

TEST(the_empty_key_has_the_offset_basis) {
    ASSERT_EQ_INT((int)2166136261u, (int)hash_string(""));
}

TEST(set_then_get) {
    struct Map m;
    map_init(&m, 16);
    ASSERT_TRUE(map_set(&m, "ada", 1));
    int out = 0;
    ASSERT_TRUE(map_get(&m, "ada", &out));
    ASSERT_EQ_INT(1, out);
    map_free(&m);
}

TEST(get_on_a_missing_key) {
    struct Map m;
    map_init(&m, 16);
    int out = 99;
    ASSERT_FALSE(map_get(&m, "nobody", &out));
    ASSERT_EQ_INT(99, out);
    map_free(&m);
}

TEST(setting_an_existing_key_replaces_it) {
    struct Map m;
    map_init(&m, 16);
    map_set(&m, "ada", 1);
    map_set(&m, "ada", 2);
    int out = 0;
    map_get(&m, "ada", &out);
    ASSERT_EQ_INT(2, out);
    ASSERT_EQ_INT(1, (int)map_count(&m));
    map_free(&m);
}

TEST(collisions_are_handled) {
    /* One bucket forces every key to collide: the chain must still work. */
    struct Map m;
    map_init(&m, 1);
    map_set(&m, "a", 1);
    map_set(&m, "b", 2);
    map_set(&m, "c", 3);
    int out = 0;
    ASSERT_TRUE(map_get(&m, "b", &out));
    ASSERT_EQ_INT(2, out);
    ASSERT_EQ_INT(3, (int)map_count(&m));
    map_free(&m);
}

TEST(the_table_copies_its_keys) {
    /* The caller's buffer is overwritten afterwards; the table must not care. */
    struct Map m;
    map_init(&m, 16);
    char key[8];
    strcpy(key, "ada");
    map_set(&m, key, 7);
    strcpy(key, "zzz");
    int out = 0;
    ASSERT_TRUE(map_get(&m, "ada", &out));
    ASSERT_EQ_INT(7, out);
    map_free(&m);
}

TEST(remove_deletes_the_entry) {
    struct Map m;
    map_init(&m, 16);
    map_set(&m, "ada", 1);
    ASSERT_TRUE(map_remove(&m, "ada"));
    ASSERT_FALSE(map_get(&m, "ada", NULL));
    ASSERT_EQ_INT(0, (int)map_count(&m));
    map_free(&m);
}

TEST(remove_from_the_middle_of_a_chain) {
    struct Map m;
    map_init(&m, 1);
    map_set(&m, "a", 1);
    map_set(&m, "b", 2);
    map_set(&m, "c", 3);
    ASSERT_TRUE(map_remove(&m, "b"));
    ASSERT_TRUE(map_get(&m, "a", NULL));
    ASSERT_TRUE(map_get(&m, "c", NULL));
    ASSERT_FALSE(map_get(&m, "b", NULL));
    map_free(&m);
}

TEST(removing_something_absent) {
    struct Map m;
    map_init(&m, 16);
    ASSERT_FALSE(map_remove(&m, "nobody"));
    map_free(&m);
}

TEST(it_holds_many_keys) {
    struct Map m;
    map_init(&m, 16);
    char key[16];
    for (int i = 0; i < 200; i++) {
        snprintf(key, sizeof key, "key%d", i);
        map_set(&m, key, i);
    }
    ASSERT_EQ_INT(200, (int)map_count(&m));
    int out = 0;
    ASSERT_TRUE(map_get(&m, "key150", &out));
    ASSERT_EQ_INT(150, out);
    map_free(&m);
}

CTEST_MAIN
