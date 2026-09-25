#include "ctest.h"
#include "bits.h"

TEST(set_adds_a_flag) {
    ASSERT_EQ_INT((int)(FLAG_READ | FLAG_WRITE),
                  (int)set_flag(FLAG_READ, FLAG_WRITE));
}

TEST(setting_an_existing_flag_changes_nothing) {
    ASSERT_EQ_INT((int)FLAG_READ, (int)set_flag(FLAG_READ, FLAG_READ));
}

TEST(clear_removes_only_that_flag) {
    unsigned perms = FLAG_READ | FLAG_WRITE | FLAG_EXEC;
    unsigned out = clear_flag(perms, FLAG_WRITE);
    ASSERT_TRUE(has_flag(out, FLAG_READ));
    ASSERT_FALSE(has_flag(out, FLAG_WRITE));
    ASSERT_TRUE(has_flag(out, FLAG_EXEC));
}

TEST(clearing_an_absent_flag_changes_nothing) {
    ASSERT_EQ_INT((int)FLAG_READ, (int)clear_flag(FLAG_READ, FLAG_EXEC));
}

TEST(toggle_flips_both_ways) {
    unsigned once = toggle_flag(0, FLAG_EXEC);
    ASSERT_TRUE(has_flag(once, FLAG_EXEC));
    ASSERT_FALSE(has_flag(toggle_flag(once, FLAG_EXEC), FLAG_EXEC));
}

TEST(has_flag_returns_one_not_the_bit) {
    /* FLAG_EXEC is 4: returning value & flag would give 4 here. */
    ASSERT_EQ_INT(1, has_flag(FLAG_EXEC, FLAG_EXEC));
    ASSERT_EQ_INT(0, has_flag(0, FLAG_EXEC));
}

TEST(counts_set_bits) {
    ASSERT_EQ_INT(0, count_bits(0));
    ASSERT_EQ_INT(1, count_bits(1));
    ASSERT_EQ_INT(3, count_bits(7));
    ASSERT_EQ_INT(1, count_bits(1u << 31));
}

TEST(counts_every_bit_set) {
    ASSERT_EQ_INT(32, count_bits(0xFFFFFFFFu));
}

TEST(extracts_each_byte) {
    unsigned value = 0xDEADBEEFu;
    ASSERT_EQ_INT(0xEF, (int)extract_byte(value, 0));
    ASSERT_EQ_INT(0xBE, (int)extract_byte(value, 1));
    ASSERT_EQ_INT(0xAD, (int)extract_byte(value, 2));
    ASSERT_EQ_INT(0xDE, (int)extract_byte(value, 3));
}

TEST(extract_rejects_an_out_of_range_index) {
    /* Shifting by 32 or more is undefined, so the guard is the lesson. */
    ASSERT_EQ_INT(0, (int)extract_byte(0xFFFFFFFFu, 4));
    ASSERT_EQ_INT(0, (int)extract_byte(0xFFFFFFFFu, -1));
}

TEST(flags_combine_and_survive_a_round_trip) {
    unsigned perms = 0;
    perms = set_flag(perms, FLAG_READ);
    perms = set_flag(perms, FLAG_EXEC);
    ASSERT_EQ_INT(2, count_bits(perms));
    perms = clear_flag(perms, FLAG_READ);
    ASSERT_EQ_INT(1, count_bits(perms));
}

CTEST_MAIN
