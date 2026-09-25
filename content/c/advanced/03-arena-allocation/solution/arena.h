#ifndef ARENA_H
#define ARENA_H

#include <stddef.h>

struct Arena {
    unsigned char *base;
    size_t capacity;
    size_t offset;
};

int arena_init(struct Arena *a, size_t capacity);
void *arena_alloc(struct Arena *a, size_t size);
char *arena_strdup(struct Arena *a, const char *s);
size_t arena_used(const struct Arena *a);
void arena_reset(struct Arena *a);
void arena_free(struct Arena *a);

#endif
