#include "cb.h"

#include <stdlib.h>
#include <string.h>

int add_op(int a, int b) { return a + b; }
int sub_op(int a, int b) { return a - b; }
int mul_op(int a, int b) { return a * b; }

/* A table beats a switch here: rows can be counted and iterated. */
static const struct {
    const char *name;
    BinaryOp fn;
} OPS[] = {
    {"add", add_op},
    {"sub", sub_op},
    {"mul", mul_op},
};

BinaryOp find_op(const char *name) {
    for (size_t i = 0; i < sizeof OPS / sizeof OPS[0]; i++) {
        if (strcmp(OPS[i].name, name) == 0) {
            return OPS[i].fn;
        }
    }
    return NULL;
}

void apply_all(int *values, int n, UnaryOp f) {
    for (int i = 0; i < n; i++) {
        values[i] = f(values[i]);
    }
}

int reduce(const int *values, int n, int initial, BinaryOp f) {
    int acc = initial;
    for (int i = 0; i < n; i++) {
        acc = f(acc, values[i]);
    }
    return acc;
}

static int compare_ints(const void *a, const void *b) {
    int x = *(const int *)a;
    int y = *(const int *)b;
    /* Not x - y: that overflows for large magnitudes and inverts the order. */
    return (x > y) - (x < y);
}

void sort_ints(int *values, int n) {
    qsort(values, (size_t)n, sizeof *values, compare_ints);
}
