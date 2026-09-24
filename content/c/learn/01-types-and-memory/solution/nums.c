#include "nums.h"

#include <limits.h>
#include <string.h>

int type_size(const char *name) {
    if (strcmp(name, "char") == 0) {
        return (int)sizeof(char);
    }
    if (strcmp(name, "int") == 0) {
        return (int)sizeof(int);
    }
    if (strcmp(name, "long") == 0) {
        return (int)sizeof(long);
    }
    if (strcmp(name, "double") == 0) {
        return (int)sizeof(double);
    }
    return -1;
}

int safe_add(int a, int b, int *out) {
    /* Checked before the addition: signed overflow is undefined, so doing it
       and inspecting the result is not a check at all. */
    if (b > 0 && a > INT_MAX - b) {
        return 0;
    }
    if (b < 0 && a < INT_MIN - b) {
        return 0;
    }
    *out = a + b;
    return 1;
}

unsigned wrap_add(unsigned a, unsigned b) {
    return a + b; /* wrapping is defined for unsigned */
}

int truncate_to_char(int value) {
    return (signed char)value;
}
