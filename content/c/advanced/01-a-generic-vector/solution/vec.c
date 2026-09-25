#include "vec.h"

#include <stdlib.h>
#include <string.h>

int vec_init(struct Vec *v, size_t elem_size) {
    if (elem_size == 0) {
        return 0;
    }
    v->data = NULL;
    v->elem_size = elem_size;
    v->count = 0;
    v->capacity = 0;
    return 1;
}

/* char* rather than void*: arithmetic on void* is a GCC extension, and a char
   is one byte by definition. */
static char *slot(const struct Vec *v, size_t index) {
    return (char *)v->data + index * v->elem_size;
}

int vec_push(struct Vec *v, const void *elem) {
    if (v->count == v->capacity) {
        size_t cap = v->capacity ? v->capacity * 2 : 4;
        /* Into a temporary: on failure realloc returns NULL and leaves the
           original allocated, so assigning back would leak it. */
        void *bigger = realloc(v->data, cap * v->elem_size);
        if (bigger == NULL) {
            return 0;
        }
        v->data = bigger;
        v->capacity = cap;
    }
    memcpy(slot(v, v->count), elem, v->elem_size);
    v->count++;
    return 1;
}

void *vec_get(const struct Vec *v, size_t index) {
    if (index >= v->count) {
        return NULL;
    }
    return slot(v, index);
}

int vec_pop(struct Vec *v, void *out) {
    if (v->count == 0) {
        return 0;
    }
    v->count--;
    if (out != NULL) {
        memcpy(out, slot(v, v->count), v->elem_size);
    }
    return 1;
}

size_t vec_count(const struct Vec *v) {
    return v->count;
}

void vec_free(struct Vec *v) {
    free(v->data);
    v->data = NULL;
    v->count = 0;
    v->capacity = 0;
}
