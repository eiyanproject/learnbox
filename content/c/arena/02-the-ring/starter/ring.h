#ifndef RING_H
#define RING_H

#define RING_CAP 4

typedef struct {
    int data[RING_CAP];
    int head;   /* index of the oldest value */
    int count;  /* how many values are stored */
} Ring;

void ring_init(Ring *r);
int ring_push(Ring *r, int value);
int ring_pop(Ring *r, int *out);
int ring_peek(const Ring *r, int index, int *out);
int ring_count(const Ring *r);

#endif
