#include "ptr.h"

#include <stddef.h>

void swap(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

void sum_and_count(const int *values, int n, int *sum_out, int *count_out) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += values[i];
    }
    /* Either result is optional: a caller that wants only one passes NULL
       for the other, and writing through it would be a crash. */
    if (sum_out != NULL) {
        *sum_out = sum;
    }
    if (count_out != NULL) {
        *count_out = n;
    }
}

int find_index(const int *values, int n, int target) {
    for (int i = 0; i < n; i++) {
        if (values[i] == target) {
            return i;
        }
    }
    return -1;
}

void increment_all(int *values, int n) {
    for (int *p = values; p < values + n; p++) {
        (*p)++;
    }
}
