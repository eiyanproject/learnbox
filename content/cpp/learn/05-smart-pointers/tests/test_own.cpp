#include "ctest.h"
#include "own.h"

#include <utility>

TEST(make_node_holds_the_value) {
    auto n = make_node(42);
    ASSERT_NOT_NULL(n.get());
    ASSERT_EQ_INT(42, n->value);
}

TEST(a_node_is_destroyed_with_its_pointer) {
    Node::live = 0;
    {
        auto n = make_node(1);
        ASSERT_EQ_INT(1, Node::live);
    }
    ASSERT_EQ_INT(0, Node::live);
}

TEST(make_nodes_numbers_them) {
    auto nodes = make_nodes(3);
    ASSERT_EQ_INT(3, (int)nodes.size());
    ASSERT_EQ_INT(0, nodes[0]->value);
    ASSERT_EQ_INT(2, nodes[2]->value);
}

TEST(make_nodes_of_zero) {
    ASSERT_TRUE(make_nodes(0).empty());
}

TEST(the_whole_vector_is_released) {
    Node::live = 0;
    {
        auto nodes = make_nodes(5);
        ASSERT_EQ_INT(5, Node::live);
    }
    ASSERT_EQ_INT(0, Node::live);
}

TEST(total_sums_the_values) {
    auto nodes = make_nodes(4);
    ASSERT_EQ_INT(0 + 1 + 2 + 3, total(nodes));
}

TEST(total_of_nothing) {
    std::vector<std::unique_ptr<Node>> empty;
    ASSERT_EQ_INT(0, total(empty));
}

TEST(take_largest_removes_and_returns_it) {
    auto nodes = make_nodes(4);
    auto biggest = take_largest(nodes);
    ASSERT_NOT_NULL(biggest.get());
    ASSERT_EQ_INT(3, biggest->value);
    ASSERT_EQ_INT(3, (int)nodes.size());
}

TEST(take_largest_transfers_ownership) {
    Node::live = 0;
    {
        auto nodes = make_nodes(3);
        auto biggest = take_largest(nodes);
        nodes.clear();
        // The vector is gone but the taken node is still alive: ownership
        // moved out rather than being copied or lost.
        ASSERT_EQ_INT(1, Node::live);
        ASSERT_EQ_INT(2, biggest->value);
    }
    ASSERT_EQ_INT(0, Node::live);
}

TEST(take_largest_of_an_empty_vector) {
    std::vector<std::unique_ptr<Node>> empty;
    ASSERT_NULL(take_largest(empty).get());
}

TEST(moving_a_unique_ptr_empties_the_source) {
    auto a = make_node(7);
    auto b = std::move(a);
    ASSERT_NULL(a.get());
    ASSERT_EQ_INT(7, b->value);
}

CTEST_MAIN
