#ifndef OWN_H
#define OWN_H

#include <memory>
#include <vector>

struct Node {
    int value;

    explicit Node(int v) : value(v) { live++; }
    ~Node() { live--; }

    // Counting live instances is how the tests prove ownership actually
    // released the memory rather than merely losing track of it.
    static int live;
};

std::unique_ptr<Node> make_node(int value);
std::vector<std::unique_ptr<Node>> make_nodes(int n);
int total(const std::vector<std::unique_ptr<Node>>& nodes);
std::unique_ptr<Node> take_largest(std::vector<std::unique_ptr<Node>>& nodes);

#endif
