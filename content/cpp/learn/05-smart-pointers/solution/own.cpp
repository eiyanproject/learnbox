#include "own.h"

#include <utility>

int Node::live = 0;

std::unique_ptr<Node> make_node(int value) {
    return std::make_unique<Node>(value);
}

std::vector<std::unique_ptr<Node>> make_nodes(int n) {
    std::vector<std::unique_ptr<Node>> nodes;
    for (int i = 0; i < n; i++) {
        // Moved in: a unique_ptr cannot be copied, and that is the guarantee.
        nodes.push_back(make_node(i));
    }
    return nodes;
}

int total(const std::vector<std::unique_ptr<Node>>& nodes) {
    int sum = 0;
    for (const auto& node : nodes) {
        sum += node->value;
    }
    return sum;
}

std::unique_ptr<Node> take_largest(std::vector<std::unique_ptr<Node>>& nodes) {
    if (nodes.empty()) {
        return nullptr;
    }
    std::size_t best = 0;
    for (std::size_t i = 1; i < nodes.size(); i++) {
        if (nodes[i]->value > nodes[best]->value) {
            best = i;
        }
    }
    std::unique_ptr<Node> taken = std::move(nodes[best]);
    nodes.erase(nodes.begin() + static_cast<long>(best));
    return taken;
}
