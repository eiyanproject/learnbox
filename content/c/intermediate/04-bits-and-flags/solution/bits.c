#include "bits.h"

unsigned set_flag(unsigned value, unsigned flag) {
    return value | flag;
}

unsigned clear_flag(unsigned value, unsigned flag) {
    return value & ~flag;
}

unsigned toggle_flag(unsigned value, unsigned flag) {
    return value ^ flag;
}

int has_flag(unsigned value, unsigned flag) {
    /* != 0 matters: value & flag is the flag's value, not 1. */
    return (value & flag) != 0;
}

int count_bits(unsigned value) {
    int count = 0;
    while (value) {
        value &= value - 1; /* clears the lowest set bit */
        count++;
    }
    return count;
}

unsigned extract_byte(unsigned value, int index) {
    if (index < 0 || index > 3) {
        return 0;
    }
    return (value >> (index * 8)) & 0xFFu;
}
