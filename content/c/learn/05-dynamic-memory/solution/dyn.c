#include "dyn.h"

#include <stdlib.h>
#include <string.h>

int *make_range(int n) {
    if (n <= 0) {
        return NULL;
    }
    int *values = malloc((size_t)n * sizeof *values);
    if (values == NULL) {
        return NULL;
    }
    for (int i = 0; i < n; i++) {
        values[i] = i;
    }
    return values;
}

char *dup_string(const char *s) {
    if (s == NULL) {
        return NULL;
    }
    size_t n = strlen(s) + 1; /* the terminator is the byte people forget */
    char *copy = malloc(n);
    if (copy == NULL) {
        return NULL;
    }
    memcpy(copy, s, n);
    return copy;
}

int *grow_array(int *values, int old_n, int new_n) {
    if (new_n <= 0) {
        free(values);
        return NULL;
    }
    /* Into a temporary: on failure realloc returns NULL and leaves the
       original allocated, so assigning straight back would leak it. */
    int *bigger = realloc(values, (size_t)new_n * sizeof *bigger);
    if (bigger == NULL) {
        return NULL;
    }
    for (int i = old_n; i < new_n; i++) {
        bigger[i] = 0;
    }
    return bigger;
}

int sum_and_free(int *values, int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += values[i];
    }
    free(values); /* free(NULL) is defined and does nothing */
    return total;
}
