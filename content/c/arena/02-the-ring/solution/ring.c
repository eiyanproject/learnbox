#include "ring.h"

void ring_init(Ring *r) {
    r->head = 0;
    r->count = 0;
}

int ring_push(Ring *r, int value) {
    if (r->count < RING_CAP) {
        r->data[(r->head + r->count) % RING_CAP] = value;
        r->count++;
        return 1;
    }
    r->data[r->head] = value;
    r->head = (r->head + 1) % RING_CAP;
    return 0;
}

int ring_pop(Ring *r, int *out) {
    if (r->count == 0) {
        return 0;
    }
    *out = r->data[r->head];
    r->head = (r->head + 1) % RING_CAP;
    r->count--;
    return 1;
}

int ring_peek(const Ring *r, int index, int *out) {
    if (index < 0 || index >= r->count) {
        return 0;
    }
    *out = r->data[(r->head + index) % RING_CAP];
    return 1;
}

int ring_count(const Ring *r) {
    return r->count;
}
