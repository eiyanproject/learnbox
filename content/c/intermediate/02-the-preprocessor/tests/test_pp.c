#include "ctest.h"
#include "pp.h"

TEST(square_of_a_simple_value) {
    ASSERT_EQ_INT(9, SQUARE(3));
}

TEST(square_of_an_expression) {
    /* Without inner parentheses this is 2 + 3 * 2 + 3 = 11. */
    ASSERT_EQ_INT(25, SQUARE(2 + 3));
}

TEST(square_combines_correctly_with_division) {
    /* Without outer parentheses this is 10 / 2 * 2 = 10. */
    ASSERT_EQ_INT(2, 10 / SQUARE(2));
}

TEST(max_and_min) {
    ASSERT_EQ_INT(5, MAX(3, 5));
    ASSERT_EQ_INT(3, MIN(3, 5));
}

TEST(max_of_expressions) {
    ASSERT_EQ_INT(7, MAX(1 + 6, 2 * 3));
}

TEST(the_macro_evaluates_the_winning_argument_twice) {
    /* ((a) > (b) ? (a) : (b)) evaluates both in the condition, then the
       chosen one again. So the winner is evaluated twice and the loser once -
       and which is which depends on the values, not on the position. */
    int calls = 0;
    int a = 1, b = 2;

    (void)MAX((calls++, a), b); /* a loses: evaluated once, in the condition */
    ASSERT_EQ_INT(1, calls);

    calls = 0;
    (void)MAX((calls++, b), a); /* b wins: condition, then again as the result */
    ASSERT_EQ_INT(2, calls);
}

TEST(the_function_evaluates_each_argument_once) {
    int calls = 0;
    int a = 1, b = 2;
    (void)safe_max((calls++, a), b);
    ASSERT_EQ_INT(1, calls);
    (void)safe_max(b, (calls++, a));
    ASSERT_EQ_INT(2, calls);
}

TEST(array_len_counts_elements) {
    int values[] = {1, 2, 3, 4};
    ASSERT_EQ_INT(4, (int)ARRAY_LEN(values));
}

TEST(array_len_of_a_char_array) {
    char buf[16];
    ASSERT_EQ_INT(16, (int)ARRAY_LEN(buf));
}

TEST(clamp_pins_both_ends) {
    ASSERT_EQ_INT(0, CLAMP(-5, 0, 10));
    ASSERT_EQ_INT(10, CLAMP(50, 0, 10));
    ASSERT_EQ_INT(7, CLAMP(7, 0, 10));
}

TEST(clamp_at_the_boundaries) {
    ASSERT_EQ_INT(0, CLAMP(0, 0, 10));
    ASSERT_EQ_INT(10, CLAMP(10, 0, 10));
}

CTEST_MAIN
