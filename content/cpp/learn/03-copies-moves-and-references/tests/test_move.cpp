#include "ctest.h"
#include "move.h"

#include <utility>
#include <vector>

TEST(a_buffer_has_the_requested_size) {
    Buffer b(10);
    ASSERT_EQ_INT(10, (int)b.size());
}

TEST(an_empty_buffer) {
    Buffer b(0);
    ASSERT_EQ_INT(0, (int)b.size());
}

TEST(copying_counts_as_a_copy) {
    Buffer::reset_counts();
    Buffer a(4);
    Buffer b(a);
    ASSERT_EQ_INT(1, Buffer::copies);
    ASSERT_EQ_INT(0, Buffer::moves);
}

TEST(a_copy_has_its_own_data) {
    Buffer a(4);
    Buffer b(a);
    ASSERT_EQ_INT(4, (int)a.size());
    ASSERT_EQ_INT(4, (int)b.size());
}

TEST(moving_counts_as_a_move) {
    Buffer::reset_counts();
    Buffer a(4);
    Buffer b(std::move(a));
    ASSERT_EQ_INT(1, Buffer::moves);
    ASSERT_EQ_INT(0, Buffer::copies);
}

TEST(a_moved_from_buffer_is_empty) {
    Buffer a(4);
    Buffer b(std::move(a));
    ASSERT_EQ_INT(4, (int)b.size());
    ASSERT_EQ_INT(0, (int)a.size());
}

TEST(copy_assignment_counts) {
    Buffer::reset_counts();
    Buffer a(2);
    Buffer b(5);
    b = a;
    ASSERT_EQ_INT(1, Buffer::copies);
    ASSERT_EQ_INT(2, (int)b.size());
}

TEST(move_assignment_counts) {
    Buffer::reset_counts();
    Buffer a(2);
    Buffer b(5);
    b = std::move(a);
    ASSERT_EQ_INT(1, Buffer::moves);
    ASSERT_EQ_INT(2, (int)b.size());
}

TEST(self_assignment_is_harmless) {
    Buffer a(3);
    a = a;
    ASSERT_EQ_INT(3, (int)a.size());
}

TEST(vector_growth_moves_rather_than_copies) {
    // The payoff for noexcept: reallocation moves the elements.
    Buffer::reset_counts();
    std::vector<Buffer> v;
    v.reserve(1);
    v.push_back(Buffer(2));
    v.push_back(Buffer(3)); // forces a reallocation
    ASSERT_EQ_INT(0, Buffer::copies);
    ASSERT_TRUE(Buffer::moves > 0);
}

CTEST_MAIN
