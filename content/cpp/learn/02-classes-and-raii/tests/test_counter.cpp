#include "ctest.h"
#include "counter.h"

#include <stdexcept>

TEST(a_new_counter_starts_at_zero) {
    Counter c;
    ASSERT_EQ_INT(0, c.value());
}

TEST(a_counter_can_start_elsewhere) {
    Counter c(10);
    ASSERT_EQ_INT(10, c.value());
}

TEST(increment_adds_one) {
    Counter c;
    c.increment();
    c.increment();
    ASSERT_EQ_INT(2, c.value());
}

TEST(add_adds_several) {
    Counter c(1);
    c.add(5);
    ASSERT_EQ_INT(6, c.value());
}

TEST(reset_returns_to_zero) {
    Counter c(7);
    c.reset();
    ASSERT_EQ_INT(0, c.value());
}

TEST(value_is_callable_on_a_const_counter) {
    // This only compiles if value() is a const member function.
    const Counter c(3);
    ASSERT_EQ_INT(3, c.value());
}

TEST(tracker_increments_on_construction) {
    int active = 0;
    {
        Tracker t(active);
        ASSERT_EQ_INT(1, active);
    }
    ASSERT_EQ_INT(0, active);
}

TEST(trackers_nest) {
    int active = 0;
    {
        Tracker a(active);
        {
            Tracker b(active);
            ASSERT_EQ_INT(2, active);
        }
        ASSERT_EQ_INT(1, active);
    }
    ASSERT_EQ_INT(0, active);
}

TEST(the_destructor_runs_on_an_early_return) {
    int active = 0;
    struct Helper {
        static void run(int& count) {
            Tracker t(count);
            return; // the destructor still runs
        }
    };
    Helper::run(active);
    ASSERT_EQ_INT(0, active);
}

TEST(the_destructor_runs_while_an_exception_unwinds) {
    int active = 0;
    try {
        Tracker t(active);
        throw std::runtime_error("boom");
    } catch (const std::runtime_error&) {
        // The tracker is gone even though the scope exited abnormally.
    }
    ASSERT_EQ_INT(0, active);
}

CTEST_MAIN
