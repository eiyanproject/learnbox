#include "arena.h"

#include <stdalign.h>
#include <stdlib.h>
#include <string.h>

int arena_init(struct Arena *a, size_t capacity) {
    if (capacity == 0) {
        return 0;
    }
    a->base = malloc(capacity);
    if (a->base == NULL) {
        return 0;
    }
    a->capacity = capacity;
    a->offset = 0;
    return 1;
}

void *arena_alloc(struct Arena *a, size_t size) {
    if (size == 0) {
        return NULL;
    }
    /* Round the offset up to the strictest alignment any standard type
       needs, so anything can be stored here. Works because alignments are
       powers of two. */
    const size_t align = alignof(max_align_t);
    size_t start = (a->offset + align - 1) & ~(align - 1);

    /* Checked this way round rather than start + size > capacity, which can
       overflow and then pass. */
    if (start > a->capacity || size > a->capacity - start) {
        return NULL;
    }
    a->offset = start + size;
    return a->base + start;
}

char *arena_strdup(struct Arena *a, const char *s) {
    if (s == NULL) {
        return NULL;
    }
    size_t n = strlen(s) + 1;
    char *copy = arena_alloc(a, n);
    if (copy == NULL) {
        return NULL;
    }
    memcpy(copy, s, n);
    return copy;
}

size_t arena_used(const struct Arena *a) {
    return a->offset;
}

void arena_reset(struct Arena *a) {
    a->offset = 0; /* nothing is freed: reusing the block is the point */
}

void arena_free(struct Arena *a) {
    free(a->base);
    a->base = NULL;
    a->capacity = 0;
    a->offset = 0;
}
