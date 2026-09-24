#ifndef COUNTER_H
#define COUNTER_H

class Counter {
public:
    explicit Counter(int start = 0) : value_(start) {}

    void increment() { value_++; }
    void add(int n) { value_ += n; }
    int value() const { return value_; }
    void reset() { value_ = 0; }

private:
    int value_;
};

// Increments the counter it is given, and decrements it on the way out -
// whether that is a normal exit, an early return, or an exception.
class Tracker {
public:
    explicit Tracker(int& count) : count_(count) { count_++; }

    ~Tracker() { count_--; }

    // A tracker owns a slot in someone else's count; copying it would
    // double-decrement, so it is not copyable.
    Tracker(const Tracker&) = delete;
    Tracker& operator=(const Tracker&) = delete;

private:
    int& count_;
};

#endif
