#include "bitset.h"

#include <string.h>

#define BYTES (BITSET_BITS / 8)

static int in_range(int n) {
    return n >= 0 && n < BITSET_BITS;
}

void bs_clear_all(BitSet *s) {
    memset(s->bytes, 0, BYTES);
}

int bs_set(BitSet *s, int n) {
    if (!in_range(n)) {
        return -1;
    }
    s->bytes[n / 8] |= (unsigned char)(1u << (n % 8));
    return 0;
}

int bs_clear(BitSet *s, int n) {
    if (!in_range(n)) {
        return -1;
    }
    s->bytes[n / 8] &= (unsigned char)~(1u << (n % 8));
    return 0;
}

int bs_test(const BitSet *s, int n) {
    if (!in_range(n)) {
        return -1;
    }
    return (s->bytes[n / 8] >> (n % 8)) & 1;
}

int bs_count(const BitSet *s) {
    int count = 0;
    for (int i = 0; i < BYTES; i++) {
        for (unsigned char b = s->bytes[i]; b; b &= (unsigned char)(b - 1)) {
            count++;  /* each pass clears the lowest set bit */
        }
    }
    return count;
}

int bs_next(const BitSet *s, int from) {
    if (from < 0) {
        from = 0;
    }
    for (int n = from; n < BITSET_BITS; n++) {
        if ((s->bytes[n / 8] >> (n % 8)) & 1) {
            return n;
        }
    }
    return -1;
}

void bs_union(BitSet *dst, const BitSet *src) {
    for (int i = 0; i < BYTES; i++) {
        dst->bytes[i] |= src->bytes[i];
    }
}

void bs_intersect(BitSet *dst, const BitSet *src) {
    for (int i = 0; i < BYTES; i++) {
        dst->bytes[i] &= src->bytes[i];
    }
}
