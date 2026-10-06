#ifndef BITSET_H
#define BITSET_H

#define BITSET_BITS 256

typedef struct {
    unsigned char bytes[BITSET_BITS / 8];
} BitSet;

void bs_clear_all(BitSet *s);
int bs_set(BitSet *s, int n);
int bs_clear(BitSet *s, int n);
int bs_test(const BitSet *s, int n);
int bs_count(const BitSet *s);
int bs_next(const BitSet *s, int from);
void bs_union(BitSet *dst, const BitSet *src);
void bs_intersect(BitSet *dst, const BitSet *src);

#endif
