#ifndef MOVE_H
#define MOVE_H

#include <cstddef>
#include <utility>
#include <vector>

class Buffer {
public:
    explicit Buffer(std::size_t n) : data_(n, 0) {}

    Buffer(const Buffer& other) : data_(other.data_) { copies++; }

    // noexcept matters: vector only moves its elements on reallocation when
    // the move constructor promises not to throw, and copies them otherwise.
    Buffer(Buffer&& other) noexcept : data_(std::move(other.data_)) { moves++; }

    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            data_ = other.data_;
            copies++;
        }
        return *this;
    }

    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            data_ = std::move(other.data_);
            moves++;
        }
        return *this;
    }

    std::size_t size() const { return data_.size(); }

    static int copies;
    static int moves;
    static void reset_counts() {
        copies = 0;
        moves = 0;
    }

private:
    std::vector<int> data_;
};

#endif
