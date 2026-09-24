#include "str.h"

int my_strlen(const char *s) {
    int n = 0;
    while (s[n] != '\0') {
        n++;
    }
    return n;
}

int copy_into(char *dst, int size, const char *src) {
    if (size <= 0) {
        return 0; /* no room even for the terminator */
    }
    int i = 0;
    while (src[i] != '\0' && i < size - 1) {
        dst[i] = src[i];
        i++;
    }
    dst[i] = '\0';
    return i;
}

int count_char(const char *s, char c) {
    int n = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] == c) {
            n++;
        }
    }
    return n;
}

void reverse_in_place(char *s) {
    int lo = 0;
    int hi = my_strlen(s) - 1;
    while (lo < hi) {
        char tmp = s[lo];
        s[lo] = s[hi];
        s[hi] = tmp;
        lo++;
        hi--;
    }
}
