#ifndef RING_H
#define RING_H

#include <array>
#include <cstddef>
#include <iterator>

template <typename T, std::size_t N>
class Ring {
    static_assert(N > 0, "a ring buffer needs room for at least one element");

public:
    using value_type = T;

    // The iterator carries a logical position, not a pointer: on a full buffer
    // the newest element sits physically before the oldest, so a "one past the
    // end" pointer would compare equal to begin().
    class const_iterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        using pointer = const T*;
        using reference = const T&;

        const_iterator() = default;
        const_iterator(const Ring* ring, std::size_t pos) : ring_(ring), pos_(pos) {}

        reference operator*() const { return (*ring_)[pos_]; }
        pointer operator->() const { return &(*ring_)[pos_]; }

        const_iterator& operator++() {
            ++pos_;
            return *this;
        }
        const_iterator operator++(int) {
            const_iterator copy = *this;
            ++pos_;
            return copy;
        }

        bool operator==(const const_iterator& other) const { return pos_ == other.pos_; }
        bool operator!=(const const_iterator& other) const { return pos_ != other.pos_; }

    private:
        const Ring* ring_ = nullptr;
        std::size_t pos_ = 0;
    };

    void push(const T& value) {
        data_[(head_ + size_) % N] = value;
        if (size_ == N) {
            head_ = (head_ + 1) % N; // full: the oldest is overwritten
        } else {
            ++size_;
        }
    }

    std::size_t size() const { return size_; }
    std::size_t capacity() const { return N; }
    bool empty() const { return size_ == 0; }
    bool full() const { return size_ == N; }

    const T& operator[](std::size_t i) const { return data_[(head_ + i) % N]; }
    T& operator[](std::size_t i) { return data_[(head_ + i) % N]; }

    const T& front() const { return (*this)[0]; }
    const T& back() const { return (*this)[size_ - 1]; }

    const_iterator begin() const { return const_iterator(this, 0); }
    const_iterator end() const { return const_iterator(this, size_); }

private:
    std::array<T, N> data_{};
    std::size_t head_ = 0;
    std::size_t size_ = 0;
};

#endif
