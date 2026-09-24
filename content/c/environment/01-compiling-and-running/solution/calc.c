#include "calc.h"

int c_max(int a, int b) {
    return a > b ? a : b;
}

int clamp(int value, int lo, int hi) {
    if (value < lo) {
        return lo;
    }
    if (value > hi) {
        return hi;
    }
    return value;
}

int is_even(int n) {
    return n % 2 == 0;
}

const char *sign_of(int n) {
    if (n < 0) {
        return "negative";
    }
    if (n == 0) {
        return "zero";
    }
    return "positive";
}
